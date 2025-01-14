fn factorial(n: int) -> int {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}


fn main() -> int {
    
    int result = factorial(5);// 5*4*3*2*1=6*20=120
    print(result);
    return 0;
}