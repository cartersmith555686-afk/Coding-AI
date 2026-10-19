"""Hand-written code templates: everyday algorithms.

Each template is a dict:
  id, title, keywords {word: weight}, langs {language: (code, precise_code_or_None, how_to_run)}
Code may contain __N__-style slots that the engine fills in (see engine.fill).
"""

TEMPLATES = []


def add(id, title, keywords, **langs):
    TEMPLATES.append({"id": id, "title": title, "keywords": keywords, "langs": langs})


add(
    "fizzbuzz", "FizzBuzz",
    {"fizzbuzz": 5, "fizz": 3, "buzz": 3, "divisible": 1, "multiples": 1},
    python=(
        '''def fizzbuzz(n):
    for i in range(1, n + 1):
        if i % 15 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)


fizzbuzz(__NUMBER|100__)
''',
        '''def fizzbuzz(n):
    """Print numbers 1..n, replacing multiples of 3/5/15 with Fizz/Buzz/FizzBuzz."""
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    for i in range(1, n + 1):
        if i % 15 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)


fizzbuzz(__NUMBER|100__)
''',
        "python fizzbuzz.py",
    ),
    javascript=(
        '''function fizzbuzz(n) {
  for (let i = 1; i <= n; i++) {
    if (i % 15 === 0) console.log("FizzBuzz");
    else if (i % 3 === 0) console.log("Fizz");
    else if (i % 5 === 0) console.log("Buzz");
    else console.log(i);
  }
}

fizzbuzz(__NUMBER|100__);
''',
        None,
        "node fizzbuzz.js",
    ),
)

add(
    "fibonacci", "Fibonacci numbers",
    {"fibonacci": 5, "fib": 4, "sequence": 1, "nth": 1},
    python=(
        '''def fibonacci(n):
    """Return the first n Fibonacci numbers."""
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence


print(fibonacci(__NUMBER|10__))
''',
        '''def fibonacci(n):
    """Return the first n Fibonacci numbers (iterative, O(n))."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence


print(fibonacci(__NUMBER|10__))
''',
        "python fibonacci.py",
    ),
    javascript=(
        '''function fibonacci(n) {
  const sequence = [];
  let a = 0, b = 1;
  for (let i = 0; i < n; i++) {
    sequence.push(a);
    [a, b] = [b, a + b];
  }
  return sequence;
}

console.log(fibonacci(__NUMBER|10__));
''',
        None,
        "node fibonacci.js",
    ),
)

add(
    "is_prime", "Prime number check",
    {"prime": 5, "primes": 5, "isprime": 5, "divisible": 1},
    python=(
        '''def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


print([n for n in range(2, __NUMBER|50__ + 1) if is_prime(n)])
''',
        None,
        "python primes.py",
    ),
    javascript=(
        '''function isPrime(n) {
  if (n < 2) return false;
  for (let i = 2; i * i <= n; i++) {
    if (n % i === 0) return false;
  }
  return true;
}

const primes = [];
for (let n = 2; n <= __NUMBER|50__; n++) if (isPrime(n)) primes.push(n);
console.log(primes);
''',
        None,
        "node primes.js",
    ),
)

add(
    "palindrome", "Palindrome check",
    {"palindrome": 6, "palindromes": 6, "reads": 1, "backwards": 2},
    python=(
        '''def is_palindrome(text):
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]


print(is_palindrome("A man, a plan, a canal: Panama"))  # True
print(is_palindrome("hello"))  # False
''',
        None,
        "python palindrome.py",
    ),
    javascript=(
        '''function isPalindrome(text) {
  const cleaned = text.toLowerCase().replace(/[^a-z0-9]/g, "");
  return cleaned === [...cleaned].reverse().join("");
}

console.log(isPalindrome("A man, a plan, a canal: Panama")); // true
console.log(isPalindrome("hello")); // false
''',
        None,
        "node palindrome.js",
    ),
)

add(
    "reverse_string", "Reverse a string",
    {"reverse": 5, "reversed": 5, "string": 2, "text": 1, "backwards": 2},
    python=(
        '''def reverse_string(text):
    return text[::-1]


print(reverse_string("hello world"))  # dlrow olleh
''',
        None,
        "python reverse.py",
    ),
    javascript=(
        '''function reverseString(text) {
  return [...text].reverse().join("");
}

console.log(reverseString("hello world")); // dlrow olleh
''',
        None,
        "node reverse.js",
    ),
)

add(
    "factorial", "Factorial",
    {"factorial": 6, "factorials": 6},
    python=(
        '''def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


print(factorial(__NUMBER|5__))
''',
        '''def factorial(n):
    """Return n! for a non-negative integer n."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


print(factorial(__NUMBER|5__))
''',
        "python factorial.py",
    ),
    javascript=(
        '''function factorial(n) {
  let result = 1n;
  for (let i = 2n; i <= BigInt(n); i++) result *= i;
  return result;
}

console.log(factorial(__NUMBER|5__).toString());
''',
        None,
        "node factorial.js",
    ),
)

add(
    "password_generator", "Random password generator",
    {"password": 5, "passwords": 5, "random": 2, "generate": 1, "generator": 1, "secure": 1},
    python=(
        '''import secrets
import string


def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


print(generate_password(__NUMBER|16__))
''',
        '''import secrets
import string


def generate_password(length=16):
    """Generate a password with at least one lowercase, uppercase, digit and symbol."""
    if length < 8:
        raise ValueError("length must be at least 8")
    symbols = "!@#$%^&*"
    pools = [string.ascii_lowercase, string.ascii_uppercase, string.digits, symbols]
    chars = [secrets.choice(pool) for pool in pools]
    everything = "".join(pools)
    chars += [secrets.choice(everything) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


print(generate_password(__NUMBER|16__))
''',
        "python password.py",
    ),
    javascript=(
        '''const { randomInt } = require("crypto");

function generatePassword(length = 16) {
  const alphabet =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
  let password = "";
  for (let i = 0; i < length; i++) {
    password += alphabet[randomInt(alphabet.length)]; // unbiased, cryptographically secure
  }
  return password;
}

console.log(generatePassword(__NUMBER|16__));
''',
        None,
        "node password.js",
    ),
)

add(
    "word_count", "Count words in text",
    {"word": 2, "words": 2, "count": 3, "frequency": 3, "occurrences": 2, "wordcount": 5},
    python=(
        '''from collections import Counter
import re


def word_count(text):
    words = re.findall(r"[a-z']+", text.lower())
    return Counter(words)


text = "the quick brown fox jumps over the lazy dog the end"
for word, count in word_count(text).most_common(5):
    print(word, count)
''',
        None,
        "python wordcount.py",
    ),
    javascript=(
        '''function wordCount(text) {
  const counts = new Map();
  for (const word of text.toLowerCase().match(/[a-z']+/g) || []) {
    counts.set(word, (counts.get(word) || 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1]);
}

const text = "the quick brown fox jumps over the lazy dog the end";
console.log(wordCount(text).slice(0, 5));
''',
        None,
        "node wordcount.js",
    ),
)
