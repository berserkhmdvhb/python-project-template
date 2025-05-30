# Environment & Logging Scenarios

This guide documents key scenarios for configuring and verifying the behavior of `.env` files, logging, and environment overrides in your CLI project. It includes both PowerShell and Linux-compatible instructions.

---

## Scenario 1: Only `.env.sample` is Present

### PowerShell

```powershell
foreach ($var in "MYPROJECT_ENV", "MYPROJECT_LOG_MAX_BYTES", "MYPROJECT_LOG_BACKUP_COUNT", "DOTENV_PATH") {
    if (Test-Path "Env:$var") { Remove-Item "Env:$var" }
}

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

## Scenario 2: No `.env` File Present

### PowerShell

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

## Scenario 3: Single `.env` File With Log Rotation

### PowerShell

```powershell
foreach ($var in "MYPROJECT_ENV", "MYPROJECT_LOG_MAX_BYTES", "MYPROJECT_LOG_BACKUP_COUNT", "DOTENV_PATH") {
    if (Test-Path "Env:$var") { Remove-Item "Env:$var" }
}

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
unset MYPROJECT_ENV MYPROJECT_LOG_MAX_BYTES MYPROJECT_LOG_BACKUP_COUNT DOTENV_PATH

cat > .env <<EOF
MYPROJECT_ENV=UAT
MYPROJECT_LOG_MAX_BYTES=100
MYPROJECT_LOG_BACKUP_COUNT=3
EOF

find . -maxdepth 1 -type f -name ".env*" ! -name ".env" -delete

myproject -q ".env file test"
```

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
