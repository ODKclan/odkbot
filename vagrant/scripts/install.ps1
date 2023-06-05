cd C:\odkbot
poetry install
icacls run.bat /grant vagrant:RX
icacls run_dev.bat /grant vagrant:RX
