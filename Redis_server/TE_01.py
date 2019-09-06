import redis

conn = redis.StrictRedis(host='localhost', port=6379, db=0)

print('Set Record:', conn.set("test", "Nice to meet you"))
print('Get Record:', conn.get("test"))
print('Delete Record:', conn.delete("test"))
print('Get Deleted Record:', conn.get("test"))