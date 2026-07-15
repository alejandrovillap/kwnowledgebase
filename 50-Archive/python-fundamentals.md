---
title: Python
date: 2026-04-19
type: reference
technology: "data-science"
status: active
tags: ["python-fundamentals", "data-structures", functions, conditionals, loops, variables]
keywords: [Python, fundamentals, variables, arithmetic, strings, conditionals, loops, functions, data structures, list, dict, tuple, set, lambda, "f-string", CCA]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Python — Fundamentos

## Salida por consola

```python
print("Hola mundo")              # texto simple
print("Hola", "Alejandro")       # múltiples argumentos, separados por espacio
print("Hola", "Ale", sep="-")    # cambia el separador → Hola-Ale
print("Sin salto", end=" ")      # evita el salto de línea al final
print(f"Merzig tiene {4} años")  # f-string: interpolación de variables
```

## Declaración de variables

Python infiere el tipo, no necesitas declararlo.

```python
nombre = "Alejandro"     # str
edad = 35                # int
altura = 1.75            # float
activo = True            # bool
nada = None              # NoneType

x, y, z = 1, 2, 3        # asignación múltiple
a = b = c = 0            # mismo valor a varias variables
```

## Operaciones aritméticas

```python
5 + 3      # 8    suma
5 - 3      # 2    resta
5 * 3      # 15   multiplicación
5 / 3      # 1.666...  división (siempre float)
5 // 3     # 1    división entera (trunca)
5 % 3      # 2    módulo (residuo)
5 ** 3     # 125  potencia
```

Operadores de asignación compuesta: `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `**=`.

## Tipos y verificación de tipo

```python
type(42)                          # <class 'int'>
isinstance(42, int)               # True
isinstance(3.14, (int, float))    # True (acepta tupla de tipos)
```

## Conversiones entre tipos (casting)

```python
int("42")          # 42
int(3.9)           # 3  (trunca, no redondea)
float("3.14")      # 3.14
str(100)           # "100"
bool(0)            # False
bool(1)            # True (cualquier valor no vacío)
list("abc")        # ['a', 'b', 'c']
```

## Funciones numéricas integradas

```python
abs(-7)             # 7
round(3.7)          # 4
round(3.14159, 2)   # 3.14
min(3, 1, 4, 1, 5)  # 1
max(3, 1, 4, 1, 5)  # 5
sum([1, 2, 3])      # 6
pow(2, 10)          # 1024
divmod(17, 5)       # (3, 2) cociente y residuo juntos
```

## Conversiones a binario, octal y hexadecimal

```python
bin(10)            # '0b1010'
oct(10)            # '0o12'
hex(255)           # '0xff'

int("1010", 2)     # 10   de binario a decimal
int("ff", 16)      # 255  de hex a decimal

bin(10)[2:]        # '1010'  (sin prefijo)
format(10, "b")    # '1010'
format(255, "x")   # 'ff'
```

## Strings (básicos)

```python
s = "Hola Mundo"

len(s)                        # 10
s.lower()                     # 'hola mundo'
s.upper()                     # 'HOLA MUNDO'
s.strip()                     # quita espacios al inicio/final
s.replace("Hola", "Adiós")   # 'Adiós Mundo'
s.split(" ")                  # ['Hola', 'Mundo']
"-".join(["a","b","c"])       # 'a-b-c'

s[0]               # 'H'   primer carácter
s[-1]              # 'o'   último carácter
s[0:4]             # 'Hola'  slicing [inicio:fin]
s[::-1]            # invertir string

"Hola" in s        # True
```

## Entrada del usuario

```python
nombre = input("¿Cómo te llamas? ")   # siempre devuelve str
edad = int(input("Edad: "))           # convertir si necesitas número
```

## Condicionales

```python
if edad >= 18:
    print("Mayor de edad")
elif edad >= 13:
    print("Adolescente")
else:
    print("Niño")

# Operador ternario
estado = "adulto" if edad >= 18 else "menor"
```

## Bucles

```python
for i in range(5):         # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):      # 1 a 5
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8
    print(i)

contador = 0
while contador < 5:
    print(contador)
    contador += 1

# Control de flujo
for i in range(10):
    if i == 3: continue    # salta esta iteración
    if i == 7: break       # sale del bucle
```

## Funciones definidas por el usuario

```python
def saludar(nombre):
    return f"Hola {nombre}"

def sumar(a, b=0):               # parámetro con valor por defecto
    return a + b

def info(*args, **kwargs):       # argumentos variables
    print(args)      # tupla
    print(kwargs)    # diccionario

# Función lambda (anónima, de una línea)
cuadrado = lambda x: x ** 2
cuadrado(5)        # 25
```

## Estructuras de datos básicas

```python
# Lista (mutable, ordenada)
frutas = ["manzana", "pera", "uva"]
frutas.append("kiwi")
frutas[0]          # 'manzana'

# Tupla (inmutable, ordenada)
punto = (3, 4)

# Diccionario (pares clave-valor)
perro = {"nombre": "Merzig", "raza": "Schnauzer"}
perro["edad"] = 5

# Conjunto (sin duplicados, sin orden)
unicos = {1, 2, 3, 3}   # {1, 2, 3}
```
