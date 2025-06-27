#!/usr/bin/env python3
import argparse
import requests
import sys
import re
import json

url = f"https://signin.aws.amazon.com/mfa"

def is_valid_email(email):
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def enum_aws_mfa_type(email):
    if not is_valid_email(email):
        print(f"Error: '{email}' is not a valid email address. Skipping.")
        return None

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {"email": email}
    try:
        #print(f"Attempting MFA enumeration for {payload} with url {url}")
        response = requests.post(url, headers=headers, data=payload)
        json_response = response.json()

        # Make sure mfaType exists
        if "mfaType" in json_response:
            mfaType = json_response["mfaType"]

            # The account has multiple types of methods registered
            if mfaType == "MULTI" and "mfaTypeList" in json_response:
                mfaTypeList = json_response["mfaTypeList"]
                mfaList = ", ".join(mfaTypeList)

                # One of those methods is U2F
                if "U2F" in mfaTypeList:
                    payload = {"email": email, "selectedMfaOption": "U2F"}
                    response = requests.post(url, headers=headers, data=payload)
                    json_response = response.json()

                    # Check if mfaSerial is present (this shouldn't happen!)
                    if "mfaSerial" in json_response:
                        mfaSerial = json_response["mfaSerial"]
                        account_id = mfaSerial.split(":")[4]
                        passkeyName = mfaSerial.split("/")[2]
                        print(f"{email}: {mfaList} - {account_id} - {passkeyName}")

                    # No key found, so just display the list of types
                    else:
                        print(f"{email}: {mfaList}")

                # U2F not in the list, so just display the list of types
                else:
                    mfaList = ", ".join(mfaTypeList)
                    print(f"{email}: {mfaList}")

            # The account only has U2F methods registered
            elif mfaType == "U2F":

                # Check if mfaSerial is present (i.e., there is only one U2F key)
                if "mfaSerial" in json_response:
                    mfaSerial = json_response["mfaSerial"]
                    account_id = mfaSerial.split(":")[4]
                    passkeyName = mfaSerial.split("/")[2]
                    print(f"{email}: {mfaType} - {account_id} - {passkeyName}")

                # No mfaSerial found (i.e., multiple keys or AWS fixed it)
                else:
                    print(f"{email}: {mfaType}")

            # The account has a single type of non-U2F method registered, so just display the type
            else:
                print(f"{email}: {mfaType}")

        else:
            print(f"Error: mfaType not in response.")

    except requests.exceptions.RequestException as e:
        print(f"Error checking MFA type for {string}: {e}")


def process_file(filename):
    try:
        with open(filename, 'r') as file:
            for line in file:
                email = line.strip()
                if email:  # Skip empty lines
                    enum_aws_mfa_type(email)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="""Enumerate the MFA type for AWS root accounts.
Provide either a single email address or a filename that contains one email per line.
A value of 'None' can mean either the account exists and does not have MFA or the account does not exist.
"""
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-e", "--email",
        help="A single email address to enumerate"
    )
    input_group.add_argument(
        "-f", "--file",
        help="Path to a file containing email addresses (one per line)"
    )

    args = parser.parse_args()

    if args.email:
        enum_aws_mfa_type(args.email)
    elif args.file:
        process_file(args.file)

if __name__ == "__main__":
    main()

