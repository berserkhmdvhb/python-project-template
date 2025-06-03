# Environment & Logging Scenarios

This guide documents key scenarios for configuring and verifying the behavior of `.env` files, logging, and environment overrides in your CLI project. It includes both PowerShell and Linux-compatible instructions. I need to make two remarks before presenting the scnearios:


1. Pleaes note that the command `make env-clear` is equivalent to following terminal command, depending on OS:

- **Windows:**

```powershell
foreach ($var in "MYPROJECT_ENV", "MYPROJECT_LOG_MAX_BYTES", "MYPROJECT_LOG_BACKUP_COUNT", "DOTENV_PATH") {
    if (Test-Path "Env:$var") { Remove-Item "Env:$var" }
}
```

- **Linux**:

```bash
unset MYPROJECT_LOG_MAX_BYTES MYPROJECT_LOG_BACKUP_COUNT DOTENV_PATH
```

2. To verify the env. variables that are active and set for this project, you can use following commands:

- **Windows:**

```powershell
Get-ChildItem Env: | Where-Object { "$($_.Name)=$($_.Value)" -like '*MYPROJECT*' }
Get-ChildItem Env: | Where-Object { $_.Name -like 'MYPROJECT_*' -or $_.Name -eq 'DOTENV_PATH' }
```

- **Linux**:

```bash
env | grep MYPROJECT
env | grep -E '^MYPROJECT_|^DOTENV_PATH='
```


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
myproject -q ".env file test" --verbose
myproject -q ".env file test" --debug

Get-Content .\logs\UAT\info.log -Tail 10
```

#### Linux

```bash
make env-clear

cat > .env.sample <<EOF
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=123456
MYPROJECT_LOG_BACKUP_COUNT=3
EOF

rm -f .env .custom.env

myproject -q ".env.sample test"
myproject -q ".env file test" --verbose
myproject -q ".env file test" --debug

tail -n 10 logs/UAT/info.log

```

---


## Scenario 2: No .env file present

1. Rest environment variables

```powershell
make env-clear
```

2. Remove all existing .env files

```powershell
Remove-Item .env* -ErrorAction SilentlyContinue
```

3. Run CLI (simple)

```powershell
myproject -q "no env file test"
```

![s2_1](https://github.com/user-attachments/assets/9e3ded20-dd0c-4796-9fd7-f29e8f8fd784)

4. Run CLI (verbose)

```powershell
myproject -q "no env file test" --verbose
```

![s2_2](https://github.com/user-attachments/assets/f9ac3cb6-abc5-4310-b1c3-89411eef7f6d)

5. Run CLI (debug)

```powershell
myproject -q "no env file test" --debug
```

![s2_3](https://github.com/user-attachments/assets/0fe89f13-42be-4ffa-8150-6184cb568e0a)

6. Verify **log rotation**: multiple logs files present

 ```powershell
Get-ChildItem .\logs\UAT\| Select-Object -ExpandProperty Name
```

![s3_4](https://github.com/user-attachments/assets/68fdc03f-02ef-40c4-b880-20e5d4639773)

### Summary
#### Powershell

```powershell
make env-clear

Remove-Item .env* -ErrorAction SilentlyContinue
myproject -q "no env file test"
```

#### Linux

```bash
make env-clear

rm -f .env*
myproject -q "no env file test"
```

---

## Scenario 3: A single .env file with log rotation automatically employed


1. Rest environment variables

```powershell
make env-clear
```

2. Remove all existing .env files

```powershell
Get-ChildItem -Path . -Filter ".env*" | Where-Object { $_.Name -ne ".env" } | Remove-Item -Force
```

3. Run CLI

```powershell
myproject -q ".env file test"
```

![s3_1](https://github.com/user-attachments/assets/dd91e614-2515-4faa-af54-f3a6a33d567c)



4. Run CLI (debug)

```powershell
myproject -q ".env file test" --debug
```

![s3_2](https://github.com/user-attachments/assets/e4e80c37-a9d3-4f4d-aec5-1a69bf810ae1)

5. Run CLI (verbose)

```powershell
myproject -q ".env file test" --verbose
```

![s3_3](https://github.com/user-attachments/assets/17c5fcbf-ed01-4208-850e-8b528eeb6797)



7. Verify **log rotation**: multiple logs files present

 ```powershell
Get-ChildItem .\logs\UAT\| Select-Object -ExpandProperty Name
```

![s3_4](https://github.com/user-attachments/assets/62bcd449-1602-4988-a61e-f58e28868670)




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
myproject -q ".env file test" --verbose
myproject -q ".env file test" --debug

Get-ChildItem .\logs\UAT\| Select-Object -ExpandProperty Name
```

#### Linux

```bash
make env-clear

cat > .env <<EOF
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=3
EOF

find . -maxdepth 1 -type f -name ".env*" ! -name ".env" -delete

myproject -q ".env file test"
myproject -q ".env file test" --verbose
myproject -q ".env file test" --debug

ls -1 logs/UAT/
```


---



## Scenario 4: Custom `custom.env` file via `DOTENV_PATH`

1. Rest environment variables

```powershell
make env-clear
```

2. Add `.custom.env` file:

```powershell
@"
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=2
"@ | Set-Content .custom.env
```

3. Remove other `.env` files

```powershell
Remove-Item .env -ErrorAction SilentlyContinue
Remove-Item .env.sample -ErrorAction SilentlyContinue
Remove-Item .env.test -ErrorAction SilentlyContinue
```

4. Run CLI (simple) with explicit `DOTENV_PATH`

```powershell
myproject -q "foo" --dotenv-path .custom.env
```

![s4_1](https://github.com/user-attachments/assets/818a49f9-73e5-4a62-a58e-f45ecf2dad5a)



5. Run CLI (verbose) with explicit `DOTENV_PATH`

```powershell
myproject -q "foo" --dotenv-path .custom.env --verbose
```

![s4_2](https://github.com/user-attachments/assets/534f448c-ea79-493d-8cf2-fc005588eb89)



6. Run CLI (debug) with explicit `DOTENV_PATH`

```powershell
myproject -q "foo" --dotenv-path .custom.env --debug
```

![s4_3](https://github.com/user-attachments/assets/c5de6a6c-6a90-4a96-8404-37c0fc25a9db)



7. Verify created log content

 ```powershell
Get-ChildItem .\logs\PROD\| Select-Object -ExpandProperty Name
```

![s4_4](https://github.com/user-attachments/assets/6509b2f9-aaa5-4c30-94de-6dfe53af2f37)



### Summary
#### Powershell

```powershell
make env-clear

@"
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=2
"@ | Set-Content .custom.env

Remove-Item .env -ErrorAction SilentlyContinue
Remove-Item .env.sample -ErrorAction SilentlyContinue
Remove-Item .env.test -ErrorAction SilentlyContinue

myproject -q "foo" --dotenv-path .custom.env
myproject -q "foo" --dotenv-path .custom.env --verbose
myproject -q "foo" --dotenv-path .custom.env --debug

Get-ChildItem .\logs\PROD\| Select-Object -ExpandProperty Name
```

#### Linux

```bash
make env-clear

cat > .custom.env <<EOF
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=2
EOF

rm -f .env .env.sample .env.test

myproject -q "foo" --dotenv-path .custom.env
myproject -q "foo" --dotenv-path .custom.env --verbose
myproject -q "foo" --dotenv-path .custom.env --debug

ls -1 logs/PROD/
```



---

## Scenario 5: Manually set environment variables override .env file values


1. Rest environment variables

```powershell
make env-clear
```

2. Create multiple .envs file with values you expect to override (they will be ignored)

- `.env`

```powershell
@"
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=1000
MYPROJECT_LOG_BACKUP_COUNT=2
"@ | Set-Content .env
```

- `custom.env`

```powershell
@"
MYPROJECT_ENV=DEV
MYPROJECT_LOG_MAX_BYTES=500
MYPROJECT_LOG_BACKUP_COUNT=2
"@ | Set-Content custom.env
```


3. Manually export an environment variable that conflicts with other .env files

```powershell
$env:MYPROJECT_ENV = "UAT"
```

4. Run CLI (simple)

```powershell
myproject -q "manual env test"
```

![s5_1](https://github.com/user-attachments/assets/56b4859b-6ef3-4d8c-a11b-26cfa9f71ff3)



5. Run CLI (verbose)

```powershell
myproject -q "manual env test" --debug
```

![s5_2](https://github.com/user-attachments/assets/0afe6a83-1d5b-4d56-92c6-ec90a13fb607)


6. Run CLI (debug)

```powershell
myproject -q "manual env test" --verbose
```

![s5_3](https://github.com/user-attachments/assets/627ff9ba-e5db-4dc6-9e4d-f07e745adc15)




7. Verify log files

 ```powershell
Get-ChildItem .\logs\UAT\| Select-Object -ExpandProperty Name
```


![s5_4](https://github.com/user-attachments/assets/a833452f-b3a9-46bc-907c-ec2d37d32648)




### Summary
#### PowerShell

```powershell
make clear-env

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
myproject -q "manual env test" --verbose
myproject -q "manual env test" --debug

Get-ChildItem .\logs\UAT\| Select-Object -ExpandProperty Name
```

#### Linux

```bash
make clear-env

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
myproject -q "manual env test" --verbose
myproject -q "manual env test" --debug

ls -1 logs/UAT/
```



---

## Scenario 6: `env.test` is automatically loaded in test context (`PYTEST_CURRENT_TEST` is set)


1. Rest environment variables

```powershell
make env-clear
```

2. Create multiple `.env` files with conflicting values

- `.env`

```powershell
@"
MYPROJECT_ENV=PROD
MYPROJECT_LOG_MAX_BYTES=5000
MYPROJECT_LOG_BACKUP_COUNT=1
"@ | Set-Content .env
```

- `.env.sample`
  
```powershell
@"
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=1000
MYPROJECT_LOG_BACKUP_COUNT=2
"@ | Set-Content .env.sample
```

- `.custom.env`

```powershell
@"
MYPROJECT_ENV=DEV
MYPROJECT_LOG_MAX_BYTES=999
MYPROJECT_LOG_BACKUP_COUNT=3
"@ | Set-Content .custom.env
```

3. Create `.env.test` with test-specific values (expected to take precedence)

```powershell
@"
MYPROJECT_ENV=TEST
MYPROJECT_LOG_MAX_BYTES=123
MYPROJECT_LOG_BACKUP_COUNT=7
"@ | Set-Content .env.test
```

4.Manually set a conflicting environment variable (should still be ignored)

`$env:MYPROJECT_ENV = "MANUAL"`

5. Simulate test context by setting `PYTEST_CURRENT_TEST`

`$env:PYTEST_CURRENT_TEST = "simulate-test"`


6. Run CLI (simple)

```powershell
myproject -q "test context env"
```

![s6_1](https://github.com/user-attachments/assets/8bc5eefb-541e-4e1f-bea0-43ad4309f81c)


7. Run CLI (verbose)

```powershell
myproject -q "test context env" --verbose
```

![s6_2](https://github.com/user-attachments/assets/d4cd24ec-a233-40fa-bdaf-6afb162b2fa3)




8. Run CLI (debug)

```powershell
myproject -q "test context env" --debug
```


![s6_3](https://github.com/user-attachments/assets/ab41efd9-c81c-40b7-a222-925c35734e7c)



7. Verify log files

 ```powershell
Get-ChildItem .\logs\TEST\| Select-Object -ExpandProperty Name
```

![s6_4](https://github.com/user-attachments/assets/9b32b556-78b2-4e82-96c1-5ad2dda63fbb)



### Summary
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
myproject -q "test context env" --verbose
myproject -q "test context env" --debug

Get-ChildItem .\logs\TEST\| Select-Object -ExpandProperty Name
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
myproject -q "test context env" --verbose
myproject -q "test context env" --debug

find logs/TEST/ -maxdepth 1 -mindepth 1 -printf "%f\n"


```


---

Each of these scenarios helps you verify priority order, file loading behavior, fallback mechanisms, and rotation logic. Adapt values as needed for your testing.
