"""More languages (C, C++, Java, Go, Rust, Lua) for the everyday algorithm templates."""
CATEGORY = "More languages"
TEMPLATES = []
RUNNABLE = {"hello_world", "fizzbuzz", "fibonacci", "factorial", "is_prime", "reverse_string", "palindrome"}
PHRASES = [
    ("fizzbuzz in c", "fizzbuzz", "c"), ("fizzbuzz in rust", "fizzbuzz", "rust"),
    ("hello world in java", "hello_world", "java"), ("prime numbers in go", "is_prime", "go"),
    ("factorial in c++", "factorial", "cpp"), ("reverse a string in lua", "reverse_string", "lua"),
    ("fibonacci in java", "fibonacci", "java"), ("palindrome check in rust", "palindrome", "rust"),
]
RUN = {
    "c": "gcc main.c -o main && ./main", "cpp": "g++ -std=c++17 main.cpp -o main && ./main",
    "java": "Save as Main.java, then: javac Main.java && java Main", "go": "go run main.go",
    "rust": "rustc main.rs && ./main", "lua": "lua main.lua (or a Script in Roblox)",
}


def L(c, cpp, java, go, rust, lua):
    return {k: (v, None, RUN[k]) for k, v in
            {"c": c, "cpp": cpp, "java": java, "go": go, "rust": rust, "lua": lua}.items()}


EXTEND = {}
EXTEND["hello_world"] = L(
    '#include <stdio.h>\n\nint main(void) {\n    printf("__REPLY|Hello, World!__\\n");\n    return 0;\n}\n',
    '#include <iostream>\n\nint main() {\n    std::cout << "__REPLY|Hello, World!__" << std::endl;\n    return 0;\n}\n',
    'public class Main {\n    public static void main(String[] args) {\n        System.out.println("__REPLY|Hello, World!__");\n    }\n}\n',
    'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("__REPLY|Hello, World!__")\n}\n',
    'fn main() {\n    println!("__REPLY|Hello, World!__");\n}\n',
    'print("__REPLY|Hello, World!__")\n')

EXTEND["fizzbuzz"] = L(
    '#include <stdio.h>\n\nint main(void) {\n    int n = __NUMBER|30__;\n    for (int i = 1; i <= n; i++) {\n        if (i % 15 == 0) printf("FizzBuzz\\n");\n        else if (i % 3 == 0) printf("Fizz\\n");\n        else if (i % 5 == 0) printf("Buzz\\n");\n        else printf("%d\\n", i);\n    }\n    return 0;\n}\n',
    '#include <iostream>\n\nint main() {\n    int n = __NUMBER|30__;\n    for (int i = 1; i <= n; i++) {\n        if (i % 15 == 0) std::cout << "FizzBuzz\\n";\n        else if (i % 3 == 0) std::cout << "Fizz\\n";\n        else if (i % 5 == 0) std::cout << "Buzz\\n";\n        else std::cout << i << "\\n";\n    }\n    return 0;\n}\n',
    'public class Main {\n    public static void main(String[] args) {\n        int n = __NUMBER|30__;\n        for (int i = 1; i <= n; i++) {\n            if (i % 15 == 0) System.out.println("FizzBuzz");\n            else if (i % 3 == 0) System.out.println("Fizz");\n            else if (i % 5 == 0) System.out.println("Buzz");\n            else System.out.println(i);\n        }\n    }\n}\n',
    'package main\n\nimport "fmt"\n\nfunc main() {\n    n := __NUMBER|30__\n    for i := 1; i <= n; i++ {\n        switch {\n        case i%15 == 0:\n            fmt.Println("FizzBuzz")\n        case i%3 == 0:\n            fmt.Println("Fizz")\n        case i%5 == 0:\n            fmt.Println("Buzz")\n        default:\n            fmt.Println(i)\n        }\n    }\n}\n',
    'fn main() {\n    let n = __NUMBER|30__;\n    for i in 1..=n {\n        if i % 15 == 0 {\n            println!("FizzBuzz");\n        } else if i % 3 == 0 {\n            println!("Fizz");\n        } else if i % 5 == 0 {\n            println!("Buzz");\n        } else {\n            println!("{}", i);\n        }\n    }\n}\n',
    'local n = __NUMBER|30__\nfor i = 1, n do\n  if i % 15 == 0 then print("FizzBuzz")\n  elseif i % 3 == 0 then print("Fizz")\n  elseif i % 5 == 0 then print("Buzz")\n  else print(i) end\nend\n')

EXTEND["fibonacci"] = L(
    '#include <stdio.h>\n\nint main(void) {\n    int n = __NUMBER|10__;\n    unsigned long long a = 0, b = 1;\n    for (int i = 0; i < n; i++) {\n        printf("%llu\\n", a);\n        unsigned long long next = a + b;\n        a = b;\n        b = next;\n    }\n    return 0;\n}\n',
    '#include <iostream>\n\nint main() {\n    int n = __NUMBER|10__;\n    unsigned long long a = 0, b = 1;\n    for (int i = 0; i < n; i++) {\n        std::cout << a << "\\n";\n        unsigned long long next = a + b;\n        a = b;\n        b = next;\n    }\n    return 0;\n}\n',
    'public class Main {\n    public static void main(String[] args) {\n        int n = __NUMBER|10__;\n        long a = 0, b = 1;\n        for (int i = 0; i < n; i++) {\n            System.out.println(a);\n            long next = a + b;\n            a = b;\n            b = next;\n        }\n    }\n}\n',
    'package main\n\nimport "fmt"\n\nfunc main() {\n    n := __NUMBER|10__\n    a, b := uint64(0), uint64(1)\n    for i := 0; i < n; i++ {\n        fmt.Println(a)\n        a, b = b, a+b\n    }\n}\n',
    'fn main() {\n    let n = __NUMBER|10__;\n    let (mut a, mut b): (u64, u64) = (0, 1);\n    for _ in 0..n {\n        println!("{}", a);\n        let next = a + b;\n        a = b;\n        b = next;\n    }\n}\n',
    'local n = __NUMBER|10__\nlocal a, b = 0, 1\nfor _ = 1, n do\n  print(a)\n  a, b = b, a + b\nend\n')

EXTEND["factorial"] = L(
    '#include <stdio.h>\n\nunsigned long long factorial(int n) {\n    unsigned long long result = 1;\n    for (int i = 2; i <= n; i++) result *= i;\n    return result;\n}\n\nint main(void) {\n    int n = __NUMBER|10__;\n    printf("%d! = %llu\\n", n, factorial(n));\n    return 0;\n}\n',
    '#include <iostream>\n\nunsigned long long factorial(int n) {\n    unsigned long long result = 1;\n    for (int i = 2; i <= n; i++) result *= i;\n    return result;\n}\n\nint main() {\n    int n = __NUMBER|10__;\n    std::cout << n << "! = " << factorial(n) << std::endl;\n    return 0;\n}\n',
    'public class Main {\n    static long factorial(int n) {\n        long result = 1;\n        for (int i = 2; i <= n; i++) result *= i;\n        return result;\n    }\n\n    public static void main(String[] args) {\n        int n = __NUMBER|10__;\n        System.out.println(n + "! = " + factorial(n));\n    }\n}\n',
    'package main\n\nimport "fmt"\n\nfunc factorial(n int) uint64 {\n    result := uint64(1)\n    for i := 2; i <= n; i++ {\n        result *= uint64(i)\n    }\n    return result\n}\n\nfunc main() {\n    n := __NUMBER|10__\n    fmt.Printf("%d! = %d\\n", n, factorial(n))\n}\n',
    'fn factorial(n: u64) -> u64 {\n    (1..=n).product()\n}\n\nfn main() {\n    let n = __NUMBER|10__;\n    println!("{}! = {}", n, factorial(n));\n}\n',
    'local function factorial(n)\n  local result = 1\n  for i = 2, n do result = result * i end\n  return result\nend\n\nlocal n = __NUMBER|10__\nprint(n .. "! = " .. factorial(n))\n')

EXTEND["is_prime"] = L(
    '#include <stdio.h>\n\nint is_prime(int n) {\n    if (n < 2) return 0;\n    for (int i = 2; (long long)i * i <= n; i++)\n        if (n % i == 0) return 0;\n    return 1;\n}\n\nint main(void) {\n    int limit = __NUMBER|50__;\n    for (int n = 2; n <= limit; n++)\n        if (is_prime(n)) printf("%d\\n", n);\n    return 0;\n}\n',
    '#include <iostream>\n\nbool is_prime(int n) {\n    if (n < 2) return false;\n    for (int i = 2; (long long)i * i <= n; i++)\n        if (n % i == 0) return false;\n    return true;\n}\n\nint main() {\n    int limit = __NUMBER|50__;\n    for (int n = 2; n <= limit; n++)\n        if (is_prime(n)) std::cout << n << "\\n";\n    return 0;\n}\n',
    'public class Main {\n    static boolean isPrime(int n) {\n        if (n < 2) return false;\n        for (int i = 2; (long) i * i <= n; i++)\n            if (n % i == 0) return false;\n        return true;\n    }\n\n    public static void main(String[] args) {\n        int limit = __NUMBER|50__;\n        for (int n = 2; n <= limit; n++)\n            if (isPrime(n)) System.out.println(n);\n    }\n}\n',
    'package main\n\nimport "fmt"\n\nfunc isPrime(n int) bool {\n    if n < 2 {\n        return false\n    }\n    for i := 2; i*i <= n; i++ {\n        if n%i == 0 {\n            return false\n        }\n    }\n    return true\n}\n\nfunc main() {\n    limit := __NUMBER|50__\n    for n := 2; n <= limit; n++ {\n        if isPrime(n) {\n            fmt.Println(n)\n        }\n    }\n}\n',
    'fn is_prime(n: u32) -> bool {\n    if n < 2 {\n        return false;\n    }\n    let mut i = 2;\n    while i * i <= n {\n        if n % i == 0 {\n            return false;\n        }\n        i += 1;\n    }\n    true\n}\n\nfn main() {\n    let limit = __NUMBER|50__;\n    for n in 2..=limit {\n        if is_prime(n) {\n            println!("{}", n);\n        }\n    }\n}\n',
    'local function isPrime(n)\n  if n < 2 then return false end\n  for i = 2, math.floor(math.sqrt(n)) do\n    if n % i == 0 then return false end\n  end\n  return true\nend\n\nfor n = 2, __NUMBER|50__ do\n  if isPrime(n) then print(n) end\nend\n')

EXTEND["reverse_string"] = L(
    '#include <stdio.h>\n#include <string.h>\n\nvoid reverse(char *s) {\n    size_t n = strlen(s);\n    for (size_t i = 0; i < n / 2; i++) {\n        char t = s[i];\n        s[i] = s[n - 1 - i];\n        s[n - 1 - i] = t;\n    }\n}\n\nint main(void) {\n    char text[] = "__REPLY|Hello, World!__";\n    reverse(text);\n    printf("%s\\n", text);\n    return 0;\n}\n',
    '#include <algorithm>\n#include <iostream>\n#include <string>\n\nint main() {\n    std::string text = "__REPLY|Hello, World!__";\n    std::reverse(text.begin(), text.end());\n    std::cout << text << std::endl;\n    return 0;\n}\n',
    'public class Main {\n    public static void main(String[] args) {\n        String text = "__REPLY|Hello, World!__";\n        System.out.println(new StringBuilder(text).reverse());\n    }\n}\n',
    'package main\n\nimport "fmt"\n\nfunc reverse(s string) string {\n    r := []rune(s)\n    for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {\n        r[i], r[j] = r[j], r[i]\n    }\n    return string(r)\n}\n\nfunc main() {\n    fmt.Println(reverse("__REPLY|Hello, World!__"))\n}\n',
    'fn main() {\n    let text = "__REPLY|Hello, World!__";\n    let reversed: String = text.chars().rev().collect();\n    println!("{}", reversed);\n}\n',
    'local text = "__REPLY|Hello, World!__"\nprint(string.reverse(text))\n')

EXTEND["palindrome"] = L(
    '#include <ctype.h>\n#include <stdio.h>\n#include <string.h>\n\nint is_palindrome(const char *s) {\n    int i = 0, j = (int)strlen(s) - 1;\n    while (i < j) {\n        while (i < j && !isalnum((unsigned char)s[i])) i++;\n        while (i < j && !isalnum((unsigned char)s[j])) j--;\n        if (tolower((unsigned char)s[i]) != tolower((unsigned char)s[j])) return 0;\n        i++;\n        j--;\n    }\n    return 1;\n}\n\nint main(void) {\n    const char *text = "__REPLY|A man, a plan, a canal: Panama__";\n    printf("%s\\n", is_palindrome(text) ? "palindrome" : "not a palindrome");\n    return 0;\n}\n',
    '#include <cctype>\n#include <iostream>\n#include <string>\n\nbool is_palindrome(const std::string &s) {\n    std::string clean;\n    for (unsigned char c : s)\n        if (std::isalnum(c)) clean += (char)std::tolower(c);\n    return std::string(clean.rbegin(), clean.rend()) == clean;\n}\n\nint main() {\n    std::string text = "__REPLY|A man, a plan, a canal: Panama__";\n    std::cout << (is_palindrome(text) ? "palindrome" : "not a palindrome") << std::endl;\n    return 0;\n}\n',
    'public class Main {\n    static boolean isPalindrome(String s) {\n        String clean = s.toLowerCase().replaceAll("[^a-z0-9]", "");\n        return new StringBuilder(clean).reverse().toString().equals(clean);\n    }\n\n    public static void main(String[] args) {\n        String text = "__REPLY|A man, a plan, a canal: Panama__";\n        System.out.println(isPalindrome(text) ? "palindrome" : "not a palindrome");\n    }\n}\n',
    'package main\n\nimport (\n    "fmt"\n    "strings"\n    "unicode"\n)\n\nfunc isPalindrome(s string) bool {\n    var r []rune\n    for _, c := range strings.ToLower(s) {\n        if unicode.IsLetter(c) || unicode.IsDigit(c) {\n            r = append(r, c)\n        }\n    }\n    for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {\n        if r[i] != r[j] {\n            return false\n        }\n    }\n    return true\n}\n\nfunc main() {\n    fmt.Println(isPalindrome("__REPLY|A man, a plan, a canal: Panama__"))\n}\n',
    'fn is_palindrome(s: &str) -> bool {\n    let clean: Vec<char> = s.chars().filter(|c| c.is_alphanumeric()).map(|c| c.to_ascii_lowercase()).collect();\n    clean.iter().eq(clean.iter().rev())\n}\n\nfn main() {\n    println!("{}", is_palindrome("__REPLY|A man, a plan, a canal: Panama__"));\n}\n',
    'local function isPalindrome(s)\n  local clean = s:lower():gsub("[^%w]", "")\n  return clean == clean:reverse()\nend\n\nprint(isPalindrome("__REPLY|A man, a plan, a canal: Panama__"))\n')
