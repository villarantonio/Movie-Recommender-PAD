# movie-recommender-embeddings

Projeto desenvolvido para a disciplina de Pensamento Analítico de Dados, onde o objetivo foi viver na prática o processo AGEMC a partir de um sistema de recomendação de filmes baseado em conteúdo.

O ponto de partida foi o dataset do MovieLens, usando gênero e tags semânticas como features principais e similaridade de cosseno para encontrar filmes parecidos. A evolução natural do projeto levou a substituir os vetorizadores clássicos (BoW, TF-IDF) por embeddings modernos, o que melhorou bastante a qualidade das recomendações — a diferença fica clara quando você compara os resultados com a lista de similares do próprio IMDB.

O processo não foi linear: a escolha das features, da medida de similaridade e do método de vetorização exigiu bastante ida e volta antes de fazer sentido. Esse caminho todo está documentado aqui, semana a semana, desde a exploração inicial dos dados até o modelo final.

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
| Integrante | Contribuição |
|---|---|
| Yago Coqueiro | Relatório de análise — foco em hipóteses, limitações metodológicas e stakeholders |
| Ivanildo Hyvo | Análise do projeto — foco em objetivo, métricas e comparação entre modelos |
| Kauã Sandes| Relatório analítico — foco em objetivo científico, respondibilidade da pergunta e consolidação das hipóteses testadas e descartadas |
---

## Próximas semanas

- [ ] Semana 2 — Estudo da Coleta e Exploração dos dados (Get + Explore)
- [ ] Semana 3 — Estudo da Implementação dos modelos e Comunicação dos resultados do projeto de referência (Model + Communication)
- [ ] Semana 4 — Definição e implementação da originalidade: qual etapa do AGEMC será modificada e como
- [ ] Semana 5 — Apresentação para a turma sobre todo o processo vivenciado
