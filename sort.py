def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        max_idx = i
        for j in range(i + 1, n):
            if arr[j] > arr[max_idx]:
                max_idx = j
        arr[i], arr[max_idx] = arr[max_idx], arr[i]
    return arr

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Examples
if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90]

    print("Array original:", data)

    print("\nBubble Sort")
    print("Descrição: compara elementos adjacentes e troca suas posições quando necessário.")
    print("Resultado:", bubble_sort(data.copy()))

    print("\nSelection Sort")
    print("Descrição: seleciona o maior elemento da parte não ordenada e o posiciona corretamente.")
    print("Resultado:", selection_sort(data.copy()))

    print("\nInsertion Sort")
    print("Descrição: insere cada elemento na posição correta dentro da parte já ordenada.")
    print("Resultado:", insertion_sort(data.copy()))

    print("\nQuick Sort")
    print("Descrição: divide a lista em torno de um pivô e ordena recursivamente as partições.")
    print("Resultado:", quick_sort(data.copy()))

    print("\nMerge Sort")
    print("Descrição: divide a lista em partes menores, ordena cada uma e depois as combina.")
    print("Resultado:", merge_sort(data.copy()))
