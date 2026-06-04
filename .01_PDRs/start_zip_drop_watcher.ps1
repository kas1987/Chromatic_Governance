param(
  [int]$IntervalSeconds = 5
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python .\pdr_zip_ingest.py watch --interval $IntervalSeconds
