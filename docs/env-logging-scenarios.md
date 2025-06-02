# Environment & Logging Scenarios

This guide documents key scenarios for configuring and verifying the behavior of `.env` files, logging, and environment overrides in your CLI project. It includes both PowerShell and Linux-compatible instructions.

---

## Scenario 1: Only `.env.sample` is Present

1. Rest environment variables

```powershell
make env-clear
```

2. Add `.env.sample` file:

```powershell
@"
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=123456
MYPROJECT_LOG_BACKUP_COUNT=3
"@ | Set-Content .env.sample
```

3. Remove other .env files

```powershell
Remove-Item .env -ErrorAction SilentlyContinue
Remove-Item .custom.env -ErrorAction SilentlyContinue
Remove-Item .env.test -ErrorAction SilentlyContinue
```

4. Run CLI (simple)

```powershell
myproject -q ".env.sample test"
```

![s1_1](https://github.com/user-attachments/assets/92f17122-6a97-48e2-99d4-03dd55de0c87)

5. Run CLI (verbose)

```powershell
myproject -q ".env.sample test" --verbose
```

![s1_2](https://github.com/user-attachments/assets/7b7fa96f-a02a-403a-8e98-dc54e4cc8b88)

6. Run CLI (debug)

```powershell
myproject -q ".env.sample test" --debug
```

![s1_3](https://github.com/user-attachments/assets/f67f75f4-4a48-4ceb-82bc-383c4e9542f7)

7. Verify created log content

 ```powershell
Get-Content .\logs\UAT\info.log -Tail 10
```

![s1_4](https://github.com/user-attachments/assets/b9f3c830-4219-4a5d-a592-84cb32279582)

### Summary
#### Powershell
```powershell
make env-clear

@"
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=123456
MYPROJECT_LOG_BACKUP_COUNT=3
"@ | Set-Content .env.sample

Remove-Item .env -ErrorAction SilentlyContinue
Remove-Item .custom.env -ErrorAction SilentlyContinue

myproject -q ".env.sample test"
```

### Linux

```bash
unset MYPROJECT_ENV MYPROJECT_LOG_MAX_BYTES MYPROJECT_LOG_BACKUP_COUNT DOTENV_PATH

cat > .env.sample <<EOF
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=123456
MYPROJECT_LOG_BACKUP_COUNT=3
EOF

rm -f .env .custom.env

myproject -q ".env.sample test"
```

---

## Scenario 2: no `.env` file present


1. Rest environment variables

```powershell
@"
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=3
"@ | Set-Content .env
```

2. Remove all existing .env files

```powershell
Get-ChildItem -Path . -Filter ".env*" | Where-Object { $_.Name -ne ".env" } | Remove-Item -Force
```

3. Run CLI

```powershell
myproject -q "no env file test"
```

![s2_1](https://github.com/user-attachments/assets/678b7cfd-fc7a-45bb-8f4b-031a231851c4)


4. Run CLI (debug)

```powershell
myproject -q "no env file test" --debug
```

![s2_2](https://github.com/user-attachments/assets/aa58b0ce-940a-4624-8259-8df6360db67c)


5. Run CLI (verbose)

```powershell
myproject -q "no env file test" --verbose
```

![s2_3](https://github.com/user-attachments/assets/b27ad41d-991a-4648-9dc6-797e25182d4d)


7. Verify created log content

 ```powershell
Get-Content .\logs\DEV\info.log -Tail 10
```

![s2_4](https://github.com/user-attachments/assets/14b19149-c0b9-4838-b4f3-d3fb9efa9588)





### Summary
#### Powershell
```powershell
foreach ($var in "MYPROJECT_ENV", "MYPROJECT_LOG_MAX_BYTES", "MYPROJECT_LOG_BACKUP_COUNT", "DOTENV_PATH") {
    if (Test-Path "Env:$var") { Remove-Item "Env:$var" }
}

Remove-Item .env* -ErrorAction SilentlyContinue
myproject -q "no env file test"
```

### Linux

```bash
unset MYPROJECT_ENV MYPROJECT_LOG_MAX_BYTES MYPROJECT_LOG_BACKUP_COUNT DOTENV_PATH

rm -f .env*
myproject -q "no env file test"
```

---

## Scenario 3: A single `.env` file with log rotation automatically employed

1. Rest environment variables

```powershell
make env-clear
```

2. Add `.env` file:

```powershell
@"
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=3
"@ | Set-Content .env.env
```

3. Remove other `.env` files

```powershell
Get-ChildItem -Path . -Filter ".env*" | Where-Object { $_.Name -ne ".env" } | Remove-Item -Force
```

4. Run CLI (simple)

```powershell
myproject -q ".env file test"
```

![s3_1](https://github.com/user-attachments/assets/68fe9d34-d08c-423f-8aa0-ba6ff7f249fa)


5. Run CLI (verbose)

```powershell
myproject -q ".env file test" --verbose
```

![s3_2](https://github.com/user-attachments/assets/8a640b01-468f-47b0-a6b0-d764516ebba0)


6. Run CLI (debug)

```powershell
myproject -q ".env file test" --debug
```

![s3_3](https://github.com/user-attachments/assets/32902cbe-4840-47bb-8f3e-6004b364c5d8)


7. Verify **log rotation**: multiple logs files present

 ```powershell
Get-ChildItem .\logs\UAT\| Select-Object -ExpandProperty Name
```

![s3_4](https://github.com/user-attachments/assets/68fdc03f-02ef-40c4-b880-20e5d4639773)


### Summary
#### Powershell
```powershell
make env-clear

@"
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=3
"@ | Set-Content .env

Get-ChildItem -Path . -Filter ".env*" | Where-Object { $_.Name -ne ".env" } | Remove-Item -Force

myproject -q ".env file test"
```

### Linux

```bash
make env-clear

cat > .env <<EOF
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=3
EOF

find . -maxdepth 1 -type f -name ".env*" ! -name ".env" -delete

myproject -q ".env file test"
```

---


















---

## Scenario 4: Custom `.env` via `DOTENV_PATH`

### PowerShell

```powershell
foreach ($var in "MYPROJECT_ENV", "MYPROJECT_LOG_MAX_BYTES", "MYPROJECT_LOG_BACKUP_COUNT", "DOTENV_PATH") {
    if (Test-Path "Env:$var") { Remove-Item "Env:$var" }
}

@"
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=2
"@ | Set-Content .custom.env

Remove-Item .env -ErrorAction SilentlyContinue
Remove-Item .env.sample -ErrorAction SilentlyContinue
Remove-Item .env.test -ErrorAction SilentlyContinue

myproject -q "foo" --dotenv-path .custom.env
```

### Linux

```bash
unset MYPROJECT_ENV MYPROJECT_LOG_MAX_BYTES MYPROJECT_LOG_BACKUP_COUNT DOTENV_PATH

cat > .custom.env <<EOF
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=2
EOF

rm -f .env .env.sample .env.test

myproject -q "foo" --dotenv-path .custom.env
```

---

## Scenario 5: Manually Set Env Variables Override `.env` Files

### PowerShell

```powershell
foreach ($var in "MYPROJECT_ENV", "MYPROJECT_LOG_MAX_BYTES", "MYPROJECT_LOG_BACKUP_COUNT", "DOTENV_PATH") {
    if (Test-Path "Env:$var") { Remove-Item "Env:$var" }
}

@"
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=1000
MYPROJECT_LOG_BACKUP_COUNT=2
"@ | Set-Content .env

@"
MYPROJECT_ENV=DEV
MYPROJECT_LOG_MAX_BYTES=500
MYPROJECT_LOG_BACKUP_COUNT=2
"@ | Set-Content custom.env

$env:MYPROJECT_ENV = "UAT"
myproject -q "manual env test"
```

### Linux

```bash
unset MYPROJECT_LOG_MAX_BYTES MYPROJECT_LOG_BACKUP_COUNT DOTENV_PATH

cat > .env <<EOF
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=1000
MYPROJECT_LOG_BACKUP_COUNT=2
EOF

cat > custom.env <<EOF
MYPROJECT_ENV=DEV
MYPROJECT_LOG_MAX_BYTES=500
MYPROJECT_LOG_BACKUP_COUNT=2
EOF

export MYPROJECT_ENV=UAT
myproject -q "manual env test"
```

---

## Scenario 6: `.env.test` Is Used in Test Context (`PYTEST_CURRENT_TEST`)

### PowerShell

```powershell
foreach ($var in "MYPROJECT_ENV", "MYPROJECT_LOG_MAX_BYTES", "MYPROJECT_LOG_BACKUP_COUNT", "DOTENV_PATH", "PYTEST_CURRENT_TEST") {
    if (Test-Path "Env:$var") { Remove-Item "Env:$var" }
}

@"
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=5000
MYPROJECT_LOG_BACKUP_COUNT=1
"@ | Set-Content .env

@"
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=1000
MYPROJECT_LOG_BACKUP_COUNT=2
"@ | Set-Content .env.sample

@"
MYPROJECT_ENV=DEV
MYPROJECT_LOG_MAX_BYTES=999
MYPROJECT_LOG_BACKUP_COUNT=3
"@ | Set-Content .custom.env

@"
MYPROJECT_ENV=TEST
MYPROJECT_LOG_MAX_BYTES=123
MYPROJECT_LOG_BACKUP_COUNT=7
"@ | Set-Content .env.test

$env:MYPROJECT_ENV = "MANUAL"
$env:PYTEST_CURRENT_TEST = "simulate-test"

myproject -q "test context env"
```

### Linux

```bash
unset MYPROJECT_LOG_MAX_BYTES MYPROJECT_LOG_BACKUP_COUNT DOTENV_PATH

cat > .env <<EOF
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=5000
MYPROJECT_LOG_BACKUP_COUNT=1
EOF

cat > .env.sample <<EOF
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=1000
MYPROJECT_LOG_BACKUP_COUNT=2
EOF

cat > .custom.env <<EOF
MYPROJECT_ENV=DEV
MYPROJECT_LOG_MAX_BYTES=999
MYPROJECT_LOG_BACKUP_COUNT=3
EOF

cat > .env.test <<EOF
MYPROJECT_ENV=TEST
MYPROJECT_LOG_MAX_BYTES=123
MYPROJECT_LOG_BACKUP_COUNT=7
EOF

export MYPROJECT_ENV=MANUAL
export PYTEST_CURRENT_TEST="simulate-test"

myproject -q "test context env"
```

---

Each of these scenarios helps you verify priority order, file loading behavior, fallback mechanisms, and rotation logic. Adapt values as needed for your testing.
