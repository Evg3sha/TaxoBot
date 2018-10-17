from tasks import add

result = add.delay(4, 4)
while not result.ready():
    pass

print(result.get(timeout=1))