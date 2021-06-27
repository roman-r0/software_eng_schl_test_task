# Software Engineering School Practical task

## Web API for bitcoin rate in UAH.

For run use python 3.8. Install requirements using:
```
pip isstall requirementst.txt
```

You could specify external API and other parameters in [config](./config.py). For correct run external API should 
return date in JSON with following format:
```
{
    'bpi': {
        'UAH': {
            'rate_float': some_float_value
        }
    }
}
```

For app run use:

```
python run.py
```

There are 3 endpoints:
1. Registration: "/user/create"
2. Sign in: "/user/login"
3. Current rate: "/btcRate"

For registration or login **email** and **password** should be given in body of request:
```
    'email: some@email
    'password': somePassword
```

After successful login user will get token, which should be used in headers (**x-access-tokens** header) to get 
bitcoin rate.

Implementation uses 2 decorators:
1. For authenticated users only when get bitcoin rate
2. For cache current rate and optimize API work (by default 10 minutes). Can be specified in [config](./config.py) 
   **CACHED_TIME**.
   
For test run with coverage run:
```
coverage run -m --source=api unittest discover
coverage report
```

No databases were used, all data stores in files. Could be specified in [config](./config.py) 
   **USERS_FILE_NAME** - for users data and **BTC_CACHE_FILE_NAME** - for bitcoin rate data.
