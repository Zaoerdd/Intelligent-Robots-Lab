@echo off
set SSH_ASKPASS=D:\Intelligent-Robots-Lab\tmp\ssh_askpass.cmd
set SSH_ASKPASS_REQUIRE=force
set DISPLAY=codex
C:\Windows\System32\OpenSSH\scp.exe -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no %*
