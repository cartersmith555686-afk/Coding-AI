"""TypeScript and C# versions of the everyday templates."""
CATEGORY = "TypeScript and C#"
TEMPLATES = []
RUNNABLE = {"hello_world", "fizzbuzz", "fibonacci", "factorial", "is_prime", "reverse_string", "palindrome"}
PHRASES = [
    ("fizzbuzz in typescript", "fizzbuzz", "typescript"), ("fizzbuzz in c#", "fizzbuzz", "csharp"),
    ("hello world in csharp", "hello_world", "csharp"), ("prime numbers in ts", "is_prime", "typescript"),
    ("factorial in c#", "factorial", "csharp"), ("reverse a string in typescript", "reverse_string", "typescript"),
    ("fibonacci in c#", "fibonacci", "csharp"), ("palindrome check in typescript", "palindrome", "typescript"),
]
TS_RUN = "npm install -g typescript, then: tsc file.ts && node file.js"
CS_RUN = "dotnet new console, paste into Program.cs, then: dotnet run"


def cs(body, usings="using System;\n"):
    return usings + "\nclass Program\n{\n" + body + "}\n"


def pair(ts, c):
    return {"typescript": (ts, None, TS_RUN), "csharp": (cs(c) if not c.startswith("using") else c, None, CS_RUN)}


EXTEND = {
    "hello_world": pair('const message: string = "__REPLY|Hello, World!__";\nconsole.log(message);\n',
                        '    static void Main()\n    {\n        Console.WriteLine("__REPLY|Hello, World!__");\n    }\n'),
    "fizzbuzz": pair(
        'function fizzbuzz(n: number): void {\n  for (let i = 1; i <= n; i++) {\n    if (i % 15 === 0) console.log("FizzBuzz");\n    else if (i % 3 === 0) console.log("Fizz");\n    else if (i % 5 === 0) console.log("Buzz");\n    else console.log(i);\n  }\n}\n\nfizzbuzz(__NUMBER|30__);\n',
        '    static void Main()\n    {\n        int n = __NUMBER|30__;\n        for (int i = 1; i <= n; i++)\n        {\n            if (i % 15 == 0) Console.WriteLine("FizzBuzz");\n            else if (i % 3 == 0) Console.WriteLine("Fizz");\n            else if (i % 5 == 0) Console.WriteLine("Buzz");\n            else Console.WriteLine(i);\n        }\n    }\n'),
    "fibonacci": pair(
        'function fibonacci(n: number): number[] {\n  const result: number[] = [];\n  let a = 0;\n  let b = 1;\n  for (let i = 0; i < n; i++) {\n    result.push(a);\n    [a, b] = [b, a + b];\n  }\n  return result;\n}\n\nconsole.log(fibonacci(__NUMBER|10__).join(", "));\n',
        '    static void Main()\n    {\n        int n = __NUMBER|10__;\n        long a = 0, b = 1;\n        for (int i = 0; i < n; i++)\n        {\n            Console.WriteLine(a);\n            long next = a + b;\n            a = b;\n            b = next;\n        }\n    }\n'),
    "factorial": pair(
        'function factorial(n: number): bigint {\n  let result = 1n;\n  for (let i = 2n; i <= BigInt(n); i++) result *= i;\n  return result;\n}\n\nconst n: number = __NUMBER|10__;\nconsole.log(`${n}! = ${factorial(n)}`);\n',
        '    static long Factorial(int n)\n    {\n        long result = 1;\n        for (int i = 2; i <= n; i++) result *= i;\n        return result;\n    }\n\n    static void Main()\n    {\n        int n = __NUMBER|10__;\n        Console.WriteLine($"{n}! = {Factorial(n)}");\n    }\n'),
    "is_prime": pair(
        'function isPrime(n: number): boolean {\n  if (n < 2) return false;\n  for (let i = 2; i * i <= n; i++) {\n    if (n % i === 0) return false;\n  }\n  return true;\n}\n\nfor (let n = 2; n <= __NUMBER|50__; n++) {\n  if (isPrime(n)) console.log(n);\n}\n',
        '    static bool IsPrime(int n)\n    {\n        if (n < 2) return false;\n        for (int i = 2; (long)i * i <= n; i++)\n            if (n % i == 0) return false;\n        return true;\n    }\n\n    static void Main()\n    {\n        int limit = __NUMBER|50__;\n        for (int n = 2; n <= limit; n++)\n            if (IsPrime(n)) Console.WriteLine(n);\n    }\n'),
    "reverse_string": pair(
        'function reverse(text: string): string {\n  return [...text].reverse().join("");\n}\n\nconsole.log(reverse("__REPLY|Hello, World!__"));\n',
        '    static void Main()\n    {\n        string text = "__REPLY|Hello, World!__";\n        char[] chars = text.ToCharArray();\n        Array.Reverse(chars);\n        Console.WriteLine(new string(chars));\n    }\n'),
    "palindrome": pair(
        'function isPalindrome(text: string): boolean {\n  const clean = text.toLowerCase().replace(/[^a-z0-9]/g, "");\n  return clean === [...clean].reverse().join("");\n}\n\nconsole.log(isPalindrome("__REPLY|A man, a plan, a canal: Panama__"));\n',
        '    static bool IsPalindrome(string text)\n    {\n        string clean = "";\n        foreach (char c in text)\n            if (char.IsLetterOrDigit(c)) clean += char.ToLower(c);\n        char[] chars = clean.ToCharArray();\n        Array.Reverse(chars);\n        return clean == new string(chars);\n    }\n\n    static void Main()\n    {\n        Console.WriteLine(IsPalindrome("__REPLY|A man, a plan, a canal: Panama__") ? "palindrome" : "not a palindrome");\n    }\n'),
}
