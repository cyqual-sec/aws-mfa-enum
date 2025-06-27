# AWS MFA Enum

This simple script attempts to enumerate the MFA status of the root user/email account of an AWS account.

If only a single U2F key (passkey) is attached to the account, AWS leaks the key's arn, including the associated AWS account ID. In such instances, this script will also parse the arn and display both the account ID and MFA serial number.

See the associated blog post for more information: [https://cyqual.com/blog/aws-mfa-account-id-enum.html](https://cyqual.com/blog/aws-mfa-account-id-enum.html)

# Usage

The script takes either a single email or a file of emails with one address per line

```bash
python aws-mfa-enum.py [-h] (-e EMAIL | -f FILE)
```

# Output Examples

Single MFA method is registered without a leaked account ID

```bash
email@domain.tld: SW
```

Multiple MFA methods are registered without a leaked account ID

```bash
email@domain.tld: MULTI - SW, U2F
```

Only a single U2F key is registered for MFA, leaking the account ID

```bash
email@domain.tld: U2F - 123456789012 - keyname-LONGKEYID
```
