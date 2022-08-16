```sh
aea create topic_aggregator --empty
aea scaffold --with-symlinks skill articles_abci
aea add connection valory/http_client:0.1.0:bafybeicmoolrrjnt5qn7jbwon7a3b5noe6hkj7kbjj57xtfosoygkckhuy --remote
aea add skill valory/abstract_round_abci:0.1.0:bafybeihcarapqbgd7czlfyygkdjvb3zxhfkxvud7hd5owajkcwqsxa63gy --remote
aea fingerprint by-path packages/arcolife/skills/articles_abci/
```
