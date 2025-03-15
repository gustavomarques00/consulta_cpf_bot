export const isValidCPF = (cpf: string): boolean => {
    cpf = cpf.replace(/\D/g, ""); // Remove caracteres não numéricos

    if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false; // Verifica se tem 11 dígitos e se não são todos iguais

    const calcDigit = (slice: string, factor: number): number => {
        const sum = slice.split("").reduce((acc, num, index) => acc + parseInt(num) * (factor - index), 0);
        const remainder = (sum * 10) % 11;
        return remainder === 10 ? 0 : remainder;
    };

    const digit1 = calcDigit(cpf.slice(0, 9), 10);
    const digit2 = calcDigit(cpf.slice(0, 10), 11);

    return digit1 === parseInt(cpf[9]) && digit2 === parseInt(cpf[10]);
};

export const formatDateTime = (): string => {
    const now = new Date();
    return now.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
};

export const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value);
};

export const formatPhone = (phone: string): string => {
    return phone.replace(/^(\d{2})(\d{5})(\d{4}).*/, "($1) $2-$3");
};

