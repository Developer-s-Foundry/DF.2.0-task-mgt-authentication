
#signup a new user

curl -X POST http://localhost:8000/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{
        "username": "mxssxn100",
        "email": "meme@example.com",
        "password": "SecretPass123!",
        "first_name": "Mx",
        "last_name": "606"
      }'


#verify email
curl "http://localhost:8000/api/users/verify-email/?token=<UUID-TOKEN-HERE>"

#login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "me@example.com", "password": "SecretPass123!"}'

# organisation, teams, teammembership, users,