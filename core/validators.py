def esta_em_branco(texto: str) -> str:
    texto_sem_espaco = texto.strip()
    if texto_sem_espaco:
        return texto
    raise ValueError('O valor não pode conter apenas espaços.')
