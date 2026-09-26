from collector import classify_command


tests = {
    "whoami": "recon",
    "id": "recon",
    "ls -la": "recon",
    "ip addr": "recon",
    "uname -a": "recon",

    "wget http://example.com/test.sh": "download",
    "curl http://example.com/test.sh": "download",

    "bash test.sh": "execution",
    "python3 script.py": "execution",
    "chmod +x test.sh": "execution",
    "mkdir test": "execution",
    "touch test.txt": "execution",

    "crontab -l": "persistence",
    "cat /etc/passwd": "credential_access",
    "cat /etc/shadow": "credential_access",

    "nc 127.0.0.1 4444": "networking",
    "ping 8.8.8.8": "networking",

    "rm test.txt": "destructive",
    "rmdir test": "destructive",

    "exit": "other",
    "cd /tmp": "other",
}


passed = 0
failed = 0


for command, expected in tests.items():
    actual = classify_command(command)

    if actual == expected:
        print(f"[PASS] {command} -> {actual}")
        passed += 1
    else:
        print(
            f"[FAIL] {command} -> "
            f"expected {expected}, got {actual}"
        )
        failed += 1


print()
print(f"Passed: {passed}")
print(f"Failed: {failed}")


if failed:
    raise SystemExit(1)
