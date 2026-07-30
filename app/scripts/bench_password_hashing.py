########################################
#               <RESUIT>               # 
# Algorithm     Hash (ms)  Verify (ms) #
# bcrypt           204.30       204.38 #
# argon2id          58.12        58.68 #
#                                      #
########################################

import time

import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

PASSWORD = "correct horse battery staple"
N = 20

start = time.perf_counter()
for _ in range(N):
    bcrypt_hash = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt())
bcrypt_hash_time = (time.perf_counter() - start) / N

start = time.perf_counter()
for _ in range(N):
    bcrypt.checkpw(PASSWORD.encode(), bcrypt_hash)
bcrypt_verify_time = (time.perf_counter() - start) / N

ph = PasswordHasher()

start = time.perf_counter()
for _ in range(N):
    argon2_hash = ph.hash(PASSWORD)
argon2_hash_time = (time.perf_counter() - start) / N

start = time.perf_counter()
for _ in range(N):
    ph.verify(argon2_hash, PASSWORD)
argon2_verify_time = (time.perf_counter() - start) / N

print(f"{'Algorithm':<10} {'Hash (ms)':>12} {'Verify (ms)':>12}")
print(f"{'bcrypt':<10} {bcrypt_hash_time * 1000:>12.2f} {bcrypt_verify_time * 1000:>12.2f}")
print(f"{'argon2id':<10} {argon2_hash_time * 1000:>12.2f} {argon2_verify_time * 1000:>12.2f}")

assert not bcrypt.checkpw(b"wrong", bcrypt_hash)
try:
    ph.verify(argon2_hash, "wrong")
    print("FAIL: argon2 should have rejected wrong password")
except VerifyMismatchError:
    print("argon2 correctly rejected wrong password")