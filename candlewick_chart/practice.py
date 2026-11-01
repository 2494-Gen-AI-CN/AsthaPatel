
# Online Python - IDE, Editor, Compiler, Interpreter

name = "helloworld"
length = int(len(name)/2)
first_half = name[:length]
second_half = name[length:]

result = first_half + second_half[::-1]
print(result)