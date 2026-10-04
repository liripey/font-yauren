# Yauren — Relatório de Controle de Qualidade

Versão 1.000 · 7 pesos (Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black) · OTF/CFF

Este relatório documenta a revisão técnica e de desenho feita como controle de qualidade da família.
Todas as verificações abaixo são reproduzíveis com `./build.sh` e as ferramentas em `tools/`.

---

## 1. Resumo

| Verificação | Ferramenta | Resultado |
|---|---|---|
| Conformidade OpenType e boas práticas (perfil *universal*) | Font Bakery | **479 aprovadas · 0 falhas · 0 alertas** (7 "erros" = serviço online de checagem de nomes indisponível no ambiente de build) |
| Contornos: sobreposições, auto-interseções, contornos minúsculos, direção | afdko `checkoutlinesufo` | **0 problemas** nos 7 pesos |
| Cobertura de idiomas | hyperglot | **376 idiomas** (348 latinos, 26 cirílicos, 2 gregos) · ≈ 3,04 bi de falantes |
| Consistência métrica entre pesos | `tools/qa_report.py` | Alturas, overshoots e métricas verticais idênticos nos 7 pesos |
| Hinting | afdko `otfautohint` | Hints e zonas de alinhamento (BlueValues) em todos os glifos |
| Renderização em corpos pequenos (10–16 px, com hinting) | FreeType + HarfBuzz | Legível em todos os pesos (ver `docs/img/03-texto.png`) |
| Recursos OpenType | feaLib + HarfBuzz | 19 recursos compilados e testados visualmente (`docs/img/05-recursos.png`) |

---

## 2. Medições por peso

| Medida | Light | Regular | Medium | SemiBold | Bold | ExtraBold | Black |
|---|---|---|---|---|---|---|---|
| haste n | 58 | 84 | 100 | 120 | 140 | 160 | 182 |
| haste H | 66 | 94 | 112 | 132 | 154 | 176 | 200 |
| fino o (topo) | 28 | 36 | 40 | 44 | 50 | 56 | 62 |
| curva o (lado) | 62 | 90 | 108 | 128 | 150 | 172 | 194 |
| contraste (fino/grosso) | 0.45 | 0.40 | 0.37 | 0.34 | 0.33 | 0.33 | 0.32 |
| altura-x | 500 | 500 | 500 | 500 | 500 | 500 | 500 |
| maiúsculas | 680 | 680 | 680 | 680 | 680 | 680 | 680 |
| ascendente / descendente | 740 / −235 | = | = | = | = | = | = |
| overshoot o / O | ±12 / ±14 | = | = | = | = | = | = |
| avanço n / o / H | 564/554/742 | 618/610/800 | 644/639/827 | 676/671/854 | 706/706/883 | 732/735/909 | 760/764/934 |
| glifos / caracteres | 814 / 728 | = | = | = | = | = | = |
| pares de kerning | 4777 | 4460 | 4346 | 4307 | 4374 | 4294 | 4324 |

Observações de controle:

* **Progressão de peso** regular: hastes crescem ≈ 16–22 unidades por passo; maiúsculas 9% mais pesadas
  que minúsculas (compensação óptica); curvas 7% mais pesadas que hastes retas (compensação de redondas).
* **Contraste** diminui suavemente nos pesos pesados (0,45 → 0,32), como em famílias de texto
  profissionais — evita que os finos desapareçam no Light e que o Black fique "manchado".
* **Overshoots** de 12/14 unidades (2,4% da altura-x) — redondas e pontas parecem do mesmo tamanho que
  as retas em todos os pesos.
* **Larguras crescem com o peso** (n: 564 → 760) para preservar as contraformas internas.
* Métricas verticais da família: hhea/typo **960/−300** com `USE_TYPO_METRICS` (entrelinha padrão
  1,26), win **967/376** cobrindo todos os glifos (sem cortes no Windows).

---

## 3. Revisão de desenho (problemas encontrados e corrigidos)

Durante o desenvolvimento cada grupo de glifos foi renderizado em grande escala (com nós e alças
visíveis) e em texto corrido nos pesos extremos. Itens identificados e corrigidos:

| # | Problema | Correção |
|---|---|---|
| 1 | Serifas fracas demais em texto (pareciam sem serifa a 16 px) | Extensão +45%, colchete mais alto, espessura de ponta aumentada |
| 2 | Colchete de serifa formava "dobra" em hastes diagonais (V, W, Y, A) | Colchete redesenhado como filete cúbico inscrito no canto — nunca ultrapassa a haste |
| 3 | União booleana em lote (skia `OpBuilder`) perdia contraformas e criava furos espúrios (ð, ƒ, ŧ, å) | Substituída por operações booleanas sequenciais + verificação automática |
| 4 | Arredondamento para inteiros gerava micro-sobreposições | Limpeza iterativa (re-simplificação até estabilizar) |
| 5 | Espaçamento: redondas apertadas (o, e, c, O, C) e maiúsculas justas | Regras ópticas: lados retos medidos da ponta da serifa, redondos do extremo da curva (≈72% do lado reto); maiúsculas 40% mais arejadas |
| 6 | Black: bojo do `a` e do `g` fechando, gotas grandes demais | Bojos maiores e traço interno mais leve nos pesos pesados; raio das gotas contido |
| 7 | Black: terminais verticais de `s S C G` virando blocos | Altura do esporão reduzida proporcionalmente ao peso |
| 8 | Black: vírgulas sob letras (ș ț ķ ļ ņ ŗ) e apóstrofo de ď ľ ť grandes demais | Escala proporcional ao peso |
| 9 | `%` e `‰` com ovais fechados no Black | Ovais redimensionados a partir da haste |
| 10 | Anel do å preenchido (espessura > raio) | Raio calculado a partir da espessura do traço |
| 11 | Gancho vietnamita (ả) com auto-interseção nos pesos pesados | Pena mais leve e gancho mais aberto |
| 12 | `fl` com colisão entre gota do f e serifa do l | Ligadura clássica: o arco do f desce como haste do l |
| 13 | Marcas combinadas vietnamitas e tonos gregos sem acesso por Unicode | Ligaduras `ccmp` e codificação U+0341/U+0344 |
| 14 | Acento de ĺ alto demais | Âncora rebaixada |
| 15 | Caudas de `j y J ŋ ђ` curtas, com gota "enrolada" | Nova cauda única: curva mais longa terminando dentro de uma gota de verdade |
| 16 | `&` com braço retangular improvisado | Bojo inferior sobe até um braço fino com serifas verticais |
| 17 | `Ta Te Tu Tr`, `Fé`, `Vá` frouxos: o bico do T impedia o encaixe | Distância mínima de kerning recalibrada; acentos continuam sem colisão |
| 18 | Esporões dos terminais de `s S C G З` viravam "degraus" nos pesos pesados | Omitidos quando ficariam menores que 18 unidades |
| 19 | `Ŋ` maiúsculo com cauda apertada (auto-sobreposição no Medium) | Cauda mais longa para proporções de maiúscula |
| 20 | `§` eram dois "S" sobrepostos com centro embolado | Redesenhado: dois "s" entrelaçados (um girado 180°) formando um laço central limpo |
| 21 | `fi` com gota do f flutuando sobre a serifa do i | fi clássico: o gancho do f se estende e a gota ocupa o lugar do pingo do i |
| 22 | `ζ` e `ξ` com barra retangular "colada" no topo | Topo em traço fino contínuo que dobra para a curva principal |
| 23 | `@` com junção confusa entre haste interna e anel | Haste do "a" interno continua, sem interrupção, no anel externo |
| 24 | `Ђ` / `Ћ` com arco estrangulado junto à haste | Corpo mais largo, arco nascendo mais baixo; cauda com gota |
| 25 | Redondas (o, c, e, d, b…) levemente frouxas no texto corrido | Espaçamento das redondas reduzido de 72% para 68% do lado reto |
| 26 | Eixo de contraste inclinado (8°) deixava O, o, 0, 8, Θ visivelmente assimétricos e entortava os cortes dos terminais (c, e, s, a…) | Eixo vertical: formas redondas espelhadas e cortes retos |
| 27 | Em alguns traços a curva passava além do ponto que devia ser o extremo (ex.: "corcunda" de 2 u no topo do `c`) | Motor corrigido: todo nó horizontal/vertical é extremo verdadeiro |
| 28 | Dimensões fracionárias geravam diferenças de 1 u entre lados de H, I, T e sinais matemáticos | Hastes, finos e contraformas inteiros e pares; largura tabular par |
| 29 | Serifas com desnível de 1 u na ponta; cunha e bicos com inclinações de 2–4° "quase retas" | Pontas planas e bicos com aresta exatamente vertical |
| 30 | Ápices e vértices (A V W v w M N Δ) fora das zonas de overshoot | Alinhados exatamente a −12/−14 e 694 |
| 31 | Pequenos desníveis: barra do e (1 u), gota do r (1 u), base do 7, junção do 2, perna do Д e Л, rabichos cirílicos tortos, cortes inclinados em α υ ψ ω, ganchos do ả e ʔ | Corrigidos individualmente |
| 32 | Microcurvas de 2–3 u com alças invertidas em junções (interior do U Black, gancho do ¿) | Eliminadas na etapa de acabamento; ordem de contornos padronizada |

---

## 4. Auditoria de simetria e retidão (`tools/audit.py`)

* **Retidão**: segmentos e alças que deveriam ser exatamente horizontais/verticais — de 1680
  ocorrências (Regular) para ≈ 20 desvios de 1–2 u em alças de curvas ajustadas, invisíveis.
* **Simetria** (glifo × seu espelho): O, o, 0, 8, H, I, T, Θ, Φ, Ω, Π, Ш, Ж, pontuação, sinais
  matemáticos e acentos (circunflexo, caron, breve, trema, mácron, anel, ponto) são **espelhados com
  exatidão**, com laterais iguais. As únicas assimetrias são as **propositais** do desenho com
  serifas: diagonais grossa/fina (A V W X Y M v w x И), serifa de cabeça em cunha (i l n u) e a
  barra do ≠.

## 5. Legibilidade — checklist

* [x] Altura-x 50% do eme (Georgia ≈ 48%, Garamond ≈ 40%)
* [x] Aberturas de `a c e s` amplas; `e` com olho grande e barra horizontal
* [x] `I` (com serifas bilaterais) ≠ `l` (serifa de cabeça em cunha) ≠ `1` (bandeira + base) ≠ `|`
* [x] `0` oval estreito ≠ `O` redondo; zero cortado opcional (`zero`)
* [x] `rn` ≠ `m` (contraformas do m menores que as do n; espaçamento entre r e n preservado)
* [x] `a` e `g` de dois andares (distinguem de `ɑ`/`q`); `α` grego com cauda (≠ `a`)
* [x] Diacríticos grandes e separados da letra (≥ 90 unidades acima da altura-x); versões próprias para maiúsculas, mais baixas
* [x] Kerning de pares críticos e de todos os acentuados com verificação de colisão (ex.: `Tô`, `Vá`, `Fé`, `“Á`)
* [x] Algarismos tabulares para tabelas, sobrescritos/subscritos reais para notação científica

---

## 6. Limitações conhecidas e recomendações

1. **Kerning** é gerado automaticamente (perfis ópticos + distância mínima). Cobre os pares críticos de
   forma consistente; recomenda-se revisar com textos reais da Yauren e acrescentar exceções para
   pares de marca específicos.
2. `ẞ` (s agudo maiúsculo, de uso raro) segue o modelo geométrico alemão e é o glifo mais simples do
   conjunto; é o próximo candidato a refinamento manual.
3. **Sem itálicos**, conforme solicitado. Uma itálica verdadeira (não inclinada artificialmente) pode
   ser derivada do mesmo motor paramétrico no futuro.
4. **Fonte variável** não foi gerada (pedido: OTF estáticos). Os 7 pesos cobrem o uso editorial.
5. **Nome "Yauren"**: o serviço de checagem de nomes do Font Bakery não pôde ser consultado neste
   ambiente — recomenda-se busca de anterioridade/registro de marca.
6. **Licença**: texto proprietário gravado nos metadados; recomenda-se revisão jurídica.
7. Teste de impressão em papel (offset/laser) nos corpos 7–9 pt antes de padronizar rótulos de amostras.

---

## 7. Como reproduzir as verificações

```bash
./build.sh                                             # gera fontes, espécimes e métricas
fontbakery check-universal fonts/otf/*.otf             # conformidade
checkoutlinesufo fonts/otf/Yauren-Regular.otf --all    # contornos (use uma cópia: a ferramenta corrige)
hyperglot fonts/otf/Yauren-Regular.otf                 # idiomas
python3 tools/qa_report.py                             # medições por peso
python3 tools/audit.py fonts/otf/Yauren-Regular.otf --sym    # retidão, alinhamento e simetria
python3 tools/charset.py fonts/otf/Yauren-Black.otf quadro.png   # quadro de glifos
```
