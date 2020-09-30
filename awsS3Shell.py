import boto3


def run_shell():
  while True:
    command = input("$ ")
    if command == "exit":
      break
    else:
       print(command)


run_shell()

