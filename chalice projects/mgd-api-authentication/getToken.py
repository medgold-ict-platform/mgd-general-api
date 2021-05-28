from warrant import Cognito, exceptions, AWSSRP
import boto3 
import sys

if __name__=="__main__":
    print(len(sys.argv))
    if len(sys.argv) < 3:
        print('Incorrect username or password')
    else:
        username=sys.argv[1]
        password=sys.argv[2]
        print(username)
        print(password)
        awssrp = AWSSRP(username, password, "eu-west-1_owfEtSFcp", pool_region="eu-west-1",client_id="7efjel0mg7qrjrvgb19dr3ooff")

        try:
            response=awssrp.authenticate_user(password)
        except exceptions.ForceChangePasswordException:
            awssrp=AWSSRP(username, password, "eu-west-1_owfEtSFcp", pool_region="eu-west-1", client_id="7efjel0mg7qrjrvgb19dr3ooff")
            awssrp.set_new_password_challenge(new_password=password)
            response = awssrp.authenticate_user(password)
            print('curl -H "Authorization: ' + response["AuthenticationResult"]["IdToken"] + '" https://api.med-gold.eu/datasets')
        except Exception:
            print('Incorrect username or password')

