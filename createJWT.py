import jwt


encoded_jwt = jwt.encode({"role": 0, "id":3}, "secret", algorithm="HS256").decode('utf-8')
decoded_jwt = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])

print(encoded_jwt)
print(decoded_jwt)