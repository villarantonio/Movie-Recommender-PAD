# Movie-Recommender

Projeto desenvolvido para a disciplina de Pensamento Analítico de Dados, onde o objetivo foi viver na prática o processo AGEMC a partir de um sistema de recomendação de filmes baseado em conteúdo.

O ponto de partida foi o dataset do MovieLens, usando gênero e tags semânticas como features principais e similaridade de cosseno para encontrar filmes parecidos. A evolução natural do projeto levou a substituir os vetorizadores clássicos (BoW, TF-IDF, LSA) por embeddings densos gerados localmente, o que melhorou a qualidade das recomendações — a diferença fica clara quando você compara os resultados com a lista de similares do próprio IMDb para *The Prestige* (2006).

O processo não foi linear: a escolha das features, da medida de similaridade e do método de vetorização exigiu bastante ida e volta antes de fazer sentido. Esse caminho todo está documentado aqui, semana a semana, desde a análise do projeto de referência até o modelo final.

---

## Referência

Prateek Gaurav — [Step By Step Content-Based Recommendation System](https://medium.com/@prateekgaurav/step-by-step-content-based-recommendation-system-823bbfd0541c) (Medium, 2023)  
Dataset: MovieLens + IMDb

---

## Semana 1 — Análise do Projeto de Referência (Ask)

A primeira semana foi dedicada a entender o projeto FMF em profundidade antes de qualquer linha de código. Cada integrante analisou o artigo de referência e respondeu às perguntas do framework AGEMC. O resultado foi consolidado no relatório analítico do grupo.

### O que foi feito

- Leitura e análise crítica do artigo de referência
- Identificação do objetivo científico, stakeholders e hipóteses
- Avaliação da respondibilidade da pergunta com os dados disponíveis
- Discussão sobre métricas de sucesso e limitações metodológicas

### Principais conclusões

**Objetivo científico**  
Construir e comparar diferentes abordagens de recomendação baseada em conteúdo — Binary Feature Matrix, BoW, TF-IDF, LSA e Word2Vec — investigando qual técnica captura melhor a similaridade semântica entre filmes. O benchmark usado foi a lista de similares do IMDb para *The Prestige* (2006).

**Descrever ou predizer?**  
O objetivo é predominantemente preditivo: dado um filme de entrada, o sistema ordena o catálogo por similaridade vetorial e retorna os mais próximos. Existe uma camada descritiva secundária na comparação entre os modelos, que é o que confere profundidade científica ao trabalho.

**A pergunta é respondível com dados?**  
Sim. *"Dado o filme X, quais filmes são mais similares por conteúdo?"* é operacionalizável — as features são estruturadas e a similaridade é computável. A limitação está na validação: o IMDb serve como proxy razoável, mas sem metodologia documentada, o que introduz um viés no critério de sucesso.

**Hipóteses testadas e descartadas**  
- ✅ Gênero sozinho gera recomendações úteis — parcialmente confirmada  
- ✅ Adicionar genome-tags melhora o resultado — confirmada  
- ✅ TF-IDF supera BoW em textos com termos raros — confirmada  
- ✅ LSA e Word2Vec pré-treinado superam abordagens de frequência — confirmada  
- ❌ Filtragem colaborativa — descartada (ausência de dados de comportamento de usuários)  
- ❌ Personalização por perfil de usuário — descartada (fora do escopo do projeto FMF)

**Métrica de sucesso**  
O projeto original não define uma métrica formal — o critério é qualitativo: comparar visualmente a lista gerada com a do IMDb. Em um contexto com maior rigor, deveriam ser usadas Precision@K, Recall@K ou NDCG sobre um conjunto de avaliações humanas, eliminando a dependência de um gabarito externo opaco.

**O que faríamos com todos os dados?**  
Com histórico de usuários (avaliações, tempo assistido) seria possível adotar filtragem colaborativa ou um modelo híbrido. Com metadados completos do IMDb (sinopses, prêmios, elenco completo) e dados contextuais, as recomendações ganhariam cobertura e personalização — atualmente limitadas pois os genome-tags cobrem apenas ~22% do catálogo.

**Stakeholders**  
- Plataformas de streaming — qual algoritmo integrar ao produto e se vale investir em modelo híbrido  
- Estúdios e distribuidoras — como posicionar filmes de nicho ao lado de títulos populares similares  
- Cientistas de dados — qual abordagem de vetorização adotar como baseline em novos projetos

### Contribuições individuais

| Integrante    | Contribuição                                                                                                                        |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Yago Coqueiro | Relatório de análise — foco em hipóteses, limitações metodológicas e stakeholders                                                   |
| Ivanildo Hyvo | Análise do projeto — foco em objetivo, métricas e comparação entre modelos                                                          |
| Kauã Sandes   | Relatório analítico — foco em objetivo científico, respondibilidade da pergunta e consolidação das hipóteses testadas e descartadas |

---

## Semana 2 — Get + Explore

A segunda semana cobriu duas etapas do AGEMC: a origem, qualidade e rastreabilidade dos dados usados no projeto FMF (**Get**) e a verificação de como o artigo conduziu, ou simplesmente deixou de conduzir, a análise exploratória antes de partir para a modelagem (**Explore**). Nas duas etapas, os quatro integrantes (Yago Coqueiro, Ivanildo Hyvo, Kauã Sandes e Luccas José) responderam às perguntas-guia correspondentes. Os relatórios de Get foram consolidados a partir da Issue #2 e complementados por uma verificação formal de licenças nas fontes oficiais, feita para resolver uma divergência encontrada entre os relatórios.

### Get — Avaliação dos Dados

#### O que foi feito

- Leitura crítica das fontes de dados do projeto FMF (MovieLens, IMDb e corpus pré-treinado do Word2Vec)
- Avaliação da suficiência dos dados frente à pergunta definida na etapa Ask
- Verificação de clareza sobre origem, período de coleta e granularidade de cada fonte
- Identificação de questões de privacidade, licença e viés na coleta
- Avaliação da reprodutibilidade e rastreabilidade do pipeline de dados original
- Verificação formal das licenças de uso (MovieLens, IMDb, Word2Vec) nas fontes oficiais, para resolver a divergência identificada nos relatórios individuais

#### Principais conclusões

**Suficiência dos dados**  
Os quatro relatórios chegam à mesma avaliação: os dados são parcialmente suficientes. MovieLens (gêneros, genome-tags, genome-scores) e IMDb (elenco, diretor, avaliações) cobrem o necessário para operacionalizar a similaridade item-item, mas a feature mais rica do modelo, as genome-tags, está presente em apenas 13.816 dos mais de 62.000 filmes do catálogo (cerca de 22%), o que reduz a abrangência real das recomendações. Yago liga esse achado diretamente à etapa Ask: mesmo respondendo à pergunta "dado o filme X, quais filmes são mais similares por conteúdo?", os dados continuam insuficientes para a pergunta de produção que de fato importa, "quais recomendações satisfazem o usuário", já que falta qualquer histórico comportamental. Luccas faz uma ressalva metodológica importante: como o artigo de referência não declara explicitamente uma pergunta do Ask, a avaliação de suficiência foi feita contra o objetivo geral do artigo, e não contra um critério fechado.

**Origem, período e granularidade**  
A origem das fontes (GroupLens/MovieLens e IMDb) é clara e pública, mas nenhum relatório encontrou indicação do período de coleta ou da versão exata usada no FMF. Luccas detalhou isso fonte por fonte: o MovieLens não informa versão nem período de coleta dos ratings, o IMDb não documenta a data do snapshot nem o processo de junção entre arquivos, e o Word2Vec pré-treinado (Google News) não menciona o período do corpus de treinamento (por volta de 2013). Sobre a granularidade, Kauã considera o nível de filme adequado; Luccas concorda que ela é razoavelmente clara para MovieLens e Word2Vec, mas ambígua no caso do dataset IMDb consolidado.

**Privacidade, licença e viés**  
Sobre privacidade, o risco é considerado baixo por todos: o MovieLens é anonimizado e os dados do IMDb são de catálogo público, sem informação pessoal de usuários. A questão de licença foi resolvida depois de uma verificação formal nas fontes oficiais (documento completo em `docs/verificacao-licencas-datasets.md`): MovieLens e IMDb restringem o uso a fins não comerciais e exigem citações e atribuições específicas que o projeto ainda não inclui — Harper & Konstan (2015) e Vig, Sen & Riedl (2012) no caso do MovieLens, e um texto de atribuição obrigatório no caso do IMDb. O Word2Vec pré-treinado, sob licença Apache 2.0, não tem essa restrição. A ação corretiva definida foi não publicar os datasets consolidados no repositório público, mantendo apenas os scripts de geração, e incluir as citações pendentes. Quanto ao viés, todos identificam a cobertura desigual das genome-tags e o viés de popularidade do IMDb, em que filmes com mais votos dominam métricas e recomendações. Kauã traz um ponto que mais ninguém levantou: o viés demográfico da própria comunidade que atribui as genome-tags no MovieLens, majoritariamente ocidental e anglófona, capaz de distorcer recomendações para certos gêneros. Luccas detalha ainda o viés cultural, temporal e de gênero presente no corpus do Word2Vec (Google News, por volta de 2013).

**Reprodutibilidade e rastreabilidade**  
O quadro é parcialmente positivo: os notebooks são versionados e públicos no GitHub. O problema é que a rastreabilidade exata do experimento fica comprometida pela falta de versionamento dos próprios datasets. Luccas mostra que o dataset IMDb consolidado (`imdb_movie_data.csv`), usado nos modelos mais avançados, nem está disponível para verificação: ele é apenas referenciado como produto de outro artigo. O Word2Vec treinado do zero tampouco tem seed ou hiperparâmetros documentados. Yago traz uma distinção importante entre as fontes: o MovieLens oferece releases numeradas e estáveis no GroupLens, o que o torna rastreável caso a versão usada seja identificada; o IMDb disponibiliza arquivos em atualização contínua e sem versionamento, o que torna o snapshot exato usado pelo autor irrecuperável.

**Conclusão da etapa Get**  
Os dados do MovieLens e do IMDb sustentam a pergunta operacional de similaridade item-item definida no Ask, mas carregam três limitações que atravessam o resto do projeto: a cobertura parcial das genome-tags, a falta de versionamento que impede reproduzir exatamente o experimento original, e as pendências de citação e atribuição de licença identificadas na verificação formal. Esses pontos foram levados em conta na etapa Explore.

### Explore — Exploração dos Dados

#### O que foi feito

- Verificação se problemas de qualidade dos dados (nulos, duplicatas, outliers) foram documentados no artigo
- Avaliação da presença (ou ausência) de análise de distribuições e correlações entre variáveis
- Identificação de padrões ou anomalias inesperadas e seu impacto sobre a pergunta original
- Discussão sobre a representatividade dos dados em relação à população de interesse

#### Principais conclusões

**Problemas de qualidade dos dados**  
O artigo não documenta nulos, duplicatas ou outliers. O único tratamento identificável no código é um `fillna('')` antes da concatenação de texto, sem nenhum registro de quantos registros foram afetados, e não existe verificação de duplicatas depois dos merges entre MovieLens e IMDb. Os outliers em variáveis numéricas, como votos e duração, também não são tratados estatisticamente. Luccas observa que eles simplesmente são convertidos em texto e absorvidos como vocabulário — o que evita o problema na prática sem de fato analisá-lo.

**Distribuições e correlações**  
Não existe EDA tradicional no artigo: nenhum histograma, estatística descritiva ou correlação entre variáveis aparece em nenhum momento. Ivanildo e Kauã destacam que o projeto pula direto para a modelagem, sem nenhuma etapa estatística que justifique as escolhas de features. Yago chama atenção para um ponto crítico: a similaridade de cosseno é justificada conceitualmente pela adequação a dados esparsos, mas essa esparsidade nunca chega a ser medida empiricamente na matriz de features gerada. O único dado distribucional que o artigo cita é isolado — cerca de 13.816 dos mais de 62.000 filmes têm genome-tags — e não há nenhuma análise de como essa cobertura varia por gênero, época ou popularidade.

**Padrões e anomalias**  
A cobertura desigual das genome-tags é o padrão que mais chama atenção dos quatro integrantes, ainda que cada um enfatize um aspecto diferente. Kauã descreve a disparidade entre filmes populares, com tags ricas, e títulos obscuros ou antigos, com scores escassos. Yago chama isso de desvantagem estrutural na matriz de similaridade para os filmes sem tags. Luccas vai um passo além e nomeia o fenômeno de "cold start" dentro dos próprios dados de conteúdo. Luccas também aponta uma segunda anomalia: o Word2Vec treinado do zero teve desempenho pior que TF-IDF, LSA e Word2Vec pré-treinado — resultado contraintuitivo, provavelmente causado por um corpus insuficiente para treinar embeddings de qualidade. Nenhuma das duas anomalias muda a pergunta original, mas ambas orientam decisões de modelagem: a cobertura desigual sugere restringir o escopo, e o resultado do Word2Vec reforça a preferência por embeddings pré-treinados em vez de treinados do zero.

**Representatividade**  
Os quatro relatos chegam ao mesmo lugar: os dados são apenas parcialmente representativos, e o artigo não entra nessa discussão. MovieLens e IMDb refletem o comportamento de usuários que avaliam filmes online, o que sub-representa produções não anglófonas e de nicho. Kauã detalha esse viés e aponta a sub-representação de cinema asiático, latino e africano em favor de produções hollywoodianas. Luccas soma a isso o fato de o sistema usar apenas metadados de itens, sem dados reais de comportamento de usuários — algo coerente com a proposta de recomendação baseada em conteúdo, mas que limita a diversidade real de preferências capturadas.

### Contribuições individuais

| Integrante    | Contribuição — Get                                                                                                                                                                | Contribuição — Explore                                                                                                          |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Yago Coqueiro | Síntese conectando a suficiência dos dados à pergunta do Ask e distinção de rastreabilidade entre MovieLens e IMDb                                                                | Lacuna metodológica da etapa exploratória e ausência de validação empírica da escolha da similaridade de cosseno               |
| Ivanildo Hyvo | Clareza de origem das fontes e riscos de uso comercial do IMDb                                                                                                                    | Ausência de EDA tradicional e limitação de cobertura das genome-tags                                                           |
| Kauã Sandes   | Viés demográfico das genome-tags e restrições de licença não comercial                                                                                                            | Disparidade de cobertura entre filmes populares e obscuros e viés geográfico/cultural do catálogo                               |
| Luccas José   | Rastreabilidade do pipeline (dataset IMDb consolidado, notebooks) e ressalva metodológica sobre suficiência sem uma pergunta do Ask explícita                                     | As duas anomalias identificadas (cobertura de tags e desempenho do Word2Vec treinado do zero) e ausência de tratamento de outliers |

---

## Semana 3 — Model + Communication + Decisão de Originalidade

A terceira semana cobriu as duas etapas restantes do projeto FMF (**Model** e **Communication**) e fechou com a decisão formal sobre qual etapa do AGEMC o grupo modificará como ponto de originalidade. Os quatro integrantes produziram relatórios individuais para cada etapa, consolidados nas Issues #3 e #4.

### Model — Avaliação dos Modelos

#### O que foi feito

- Análise da justificativa algorítmica dos modelos escolhidos no FMF
- Verificação da presença (ou ausência) de separação entre dados de treino e teste
- Avaliação das métricas usadas e se elas refletem o custo real dos erros no contexto do problema
- Análise da interpretabilidade dos modelos e sua implicação para a confiança dos stakeholders

#### Principais conclusões

**Justificativa algorítmica — teoricamente coerente, empiricamente fraca**  
A progressão Binary Feature Matrix → BoW → TF-IDF → LSA → Word2Vec segue uma lógica pedagógica válida, e a escolha da similaridade de cosseno é conceitualmente adequada para dados esparsos. O problema, apontado pelos quatro integrantes, é que o artigo nunca mede a esparsidade real da matriz gerada — a justificativa permanece teórica. A seleção do LSA como modelo superior é declarada com base em inspeção visual, sem critério reproduzível (Luccas).

**Separação treino/teste — ausente, mas parcialmente justificável**  
Não existe nenhuma divisão entre dados de treino e teste em nenhum dos cinco notebooks. Yago aponta que isso não é necessariamente um erro metodológico — sistemas baseados em conteúdo não se enquadram perfeitamente no paradigma supervisionado — mas a ausência de qualquer holdout impede avaliar se as relações de similaridade generalizam para filmes fora do catálogo original. Luccas reforça que o projeto sequer levanta essa questão.

**Métricas — inexistentes como medida formal**  
Não há Precision@K, Recall@K, NDCG ou qualquer medida quantitativa. A única avaliação é qualitativa: comparar a saída de cada modelo com a lista de similares do IMDb para *The Prestige* (2006). Kauã e Luccas destacam que esse processo não distingue a gravidade dos erros — recomendar um filme de gênero totalmente diferente tem o mesmo peso que errar uma nuance de tom, que é peso nulo. Em um cenário real de produção, isso é uma falha grave.

**Interpretabilidade — ponto forte, mas insuficiente sozinho**  
Modelos simples como TF-IDF são transparentes e auditáveis. O problema, levantado por Kauã e Ivanildo, é que os modelos com melhor desempenho (LSA e Word2Vec) funcionam como caixas-pretas. Há uma tensão real entre desempenho e confiança: os modelos mais explicáveis recomendam pior, e os que recomendam melhor são os mais difíceis de justificar — trade-off que o artigo não trata. Yago resume o limite dessa situação: a interpretabilidade explica *como* o modelo chegou a uma recomendação, mas não diz se aquela recomendação é, em qualquer sentido mensurável, boa.

### Communication — Avaliação da Comunicação dos Resultados

#### O que foi feito

- Verificação se a narrativa conecta os achados à pergunta feita no Ask
- Avaliação das visualizações e sua adequação ao público-alvo
- Verificação se as limitações e incertezas do modelo foram comunicadas de forma honesta
- Análise das recomendações e próximos passos apresentados

#### Principais conclusões

**Narrativa e conexão com o Ask — implícita, mas presente**  
Os quatro integrantes chegaram ao mesmo diagnóstico: o artigo nunca formula explicitamente a pergunta de pesquisa, mas a estrutura progressiva dos experimentos cria um fio condutor implícito. O leitor entende o que está sendo comparado, mas precisa montar a síntese final sozinho — não há uma seção de conclusão que amarre os cinco experimentos a uma resposta direta. Yago observa que isso não desestrutura o texto, mas enfraquece o fechamento do raciocínio.

**Visualizações — adequadas para público técnico, insuficientes para stakeholders**  
Convergência total: o artigo usa apenas tabelas de saída de código e trechos de Python, sem gráficos que permitam comparar o desempenho dos modelos de forma rápida. Para um cientista de dados que acompanha o código, isso funciona. Para gestores de plataforma ou executivos de estúdio — stakeholders identificados na etapa Ask — a ausência de visualização sintética é uma barreira real. Termos como TF-IDF, LSA e similaridade de cosseno aparecem sem definição acessível.

**Limitações — comunicadas de forma seletiva**  
Yago, Kauã e Ivanildo apontaram que o artigo comunica as limitações apenas em parte, cobrindo a cobertura das genome-tags mas deixando de fora a ausência de métrica formal, a validação baseada em um único filme e o IMDb como gabarito opaco. Luccas identificou uma seção dedicada a limitações com seis pontos — o que sugere que parte das omissões pode estar em notebooks específicos, não no artigo completo.

**Recomendações acionáveis — presentes, mas com escopo técnico restrito**  
O artigo aponta caminhos concretos: aumentar o volume de dados, usar metadados adicionais do IMDb, explorar modelos híbridos. Esses são próximos passos para quem vai replicar o experimento. Faltam recomendações orientadas a decisão: qual técnica adotar em produção considerando custo computacional, como tratar a desigualdade de cobertura das genome-tags antes de um eventual deploy, qual o custo aceitável de erro por posição na lista. Yago resume bem: o trabalho é mais um relato de processo experimental do que um relatório orientado à tomada de decisão.

### Decisão de Originalidade — Etapa M (Model)

O grupo optou por modificar a etapa **M — Model**. No FMF, a vetorização passa por cinco técnicas, com LSA como melhor resultado. Nossa modificação substitui essa camada inteira por embeddings densos gerados localmente via um modelo pré-treinado da família BGE (`BAAI/bge-large-en-v1.5` ou equivalente), mantendo o restante do pipeline idêntico: similaridade de cosseno, top-N de recomendações e benchmark com a lista do IMDb para *The Prestige* (2006).

A justificativa tem três pilares. Primeiro, embeddings BGE são otimizados para similaridade semântica — foram treinados com objetivos de retrieval e ranking, não apenas de modelagem de linguagem, o que é diretamente relevante para o problema de similaridade item-item. Segundo, a representação é densa, o que elimina o problema de esparsidade presente em todos os vetorizadores do FMF. Terceiro, o modelo tem documentação técnica publicada e benchmarks padronizados (MTEB), tornando a escolha verificável e reproduzível — ao contrário do Word2Vec treinado no Google News, que não documenta período nem hiperparâmetros.

A comparabilidade com o FMF é preservada integralmente: mesma entrada, mesmo gabarito, mesma medida de similaridade. A única diferença é o vetor que representa cada filme — que é exatamente o que queremos medir.

### Contribuições individuais

| Integrante    | Contribuição — Model                                                                                                                                          | Contribuição — Communication                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Yago Coqueiro | Justificativa algorítmica, ausência de validação fora da amostra e limite da interpretabilidade sem métrica                                                   | Narrativa implícita, comunicação seletiva das limitações e escopo restrito das recomendações                        |
| Kauã Sandes   | Trade-off desempenho/interpretabilidade e ausência de distinção entre tipos de erro                                                                           | Jargão não traduzido, visualizações insuficientes para stakeholders não técnicos e acionabilidade fraca             |
| Ivanildo Hyvo | Coerência algorítmica e interpretabilidade diferenciada por tipo de modelo (TF-IDF vs. Word2Vec)                                                              | Narrativa sem pergunta explícita e limitações comunicadas apenas em parte                                           |
| Luccas José   | Justificativa sem critério reproduzível, ausência de separação treino/teste e interpretabilidade sem evidência de qualidade                                   | Narrativa dispersa, limitações com seção dedicada identificada e recomendações técnicas sem orientação à decisão    |
| Antonio       | Consolidação dos relatórios M e C, decisão formal de originalidade e documentação                                                                             |                                                                                                                     |

---

## Próximas semanas

- [x] Semana 1 — Análise do Projeto de Referência (Ask)
- [x] Semana 2 — Coleta e Exploração dos dados (Get + Explore)
- [x] Semana 3 — Modelos, Comunicação e Decisão de Originalidade (Model + Communication)

## Semana 4 — Apresentação Final

Por acordo entre os grupos da disciplina, a apresentação foi antecipada para o dia **25/06/2026**. As etapas de implementação da originalidade (embeddings BGE) e comunicação final dos resultados serão apresentadas nessa data, consolidando todo o processo AGEMC vivenciado pelo grupo ao longo do projeto.
