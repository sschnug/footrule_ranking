# Intro
This code solves the *Spearman Footrule (Rank Aggregation) problem* ([overview slides](http://theory.stanford.edu/~sergei/slides/www10-metrics.pdf)) exactly.

The approach used is based on:

> Dwork, Cynthia, et al. "Rank aggregation methods for the web." Proceedings of the 10th international conference on World Wide Web. ACM, 2001.

formulating the problem as [Minimum-Cost Bipartite Matching](http://theory.stanford.edu/~tim/w16/l/l5.pdf) problem, which is then solved by Linear-Programming using *cylp*. The LP-formulation is well-known and for example described [here](http://www.cs.cornell.edu/courses/cs6820/2010fa/handouts/matchings.pdf).

Others approached this with the Linear-assignment problem and the [Hungarian-algorithm](https://en.wikipedia.org/wiki/Hungarian_algorithm) which might be a more dedicated method.

I have chosen to use an LP-approach because:

- (Available) LP-solvers are high-quality nowadays (especially compared to less general problems like the Assignment-problem)
  - It's not impossible to observe LP-solvers beat the Hungarian-algorithm for larger instances (unscientific remark!)
- This code might be reused as component in an LP-based branch-and-bound algorithm for the *Kemeny Rank Aggregation* problem in the future, trying to compete with the off-the-shelf MIP-based approach [here](https://github.com/sschnug/kemeny_ranking)
  - Both bounds could be computed by LP:
    - lower: kemeny-MIP relaxed
    - upper: footrule-LP (which holds theoretical approximation guarantees in regards to the optimal kemeny-score; see paper!)
  - In this approach it is of utter importance to make use of efficient **warm-starting**, supported by LP-solvers!

# Requirements / Software used
The code uses:
- python (only py3 tested)
- python's scientific stack (numpy, scipy)
- [cylp](https://github.com/coin-or/CyLP) as interface to the solver
- [CoinOR Clp](https://projects.coin-or.org/Clp) as the (imho best free open-source) core LP-solver

# Status
- Prototype-like code
- Not much input-specification / checking
- No support for ties / incomplete votes
- Preprocessing and some other parts are non-vectorized / slow at the moment

# Example

**example_ski_jumping.txt**:

    A: GregorSchlierenzauer SimonAmmann WolfgangLoitzl HarriOlli DimitryVassiliev MartinSchmitt ThomasMorgenstern MartinKoch AndersBardal AndreasKüttel AdamMalysz NoriakiKasai EmmanuelChedal MichaelUhrmann MichaelNeumayer JakubJanda RobertKranjec TomHilde TakanobuOkabe DaikiIto DenisKornilov KamilStoch StephanHocke AndreasKofler JernejDamjan SebastianColloredo StefanHula SigurdPettersen PrimozPeterka PrimozPikl ManuelFettner JanMatura JonAaraas
    B: ThomasMorgenstern GregorSchlierenzauer TomHilde AndersBardal AndreasKüttel SimonAmmann WolfgangLoitzl AdamMalysz AndreasKofler MartinKoch JernejDamjan MichaelNeumayer DimitryVassiliev MartinSchmitt DenisKornilov EmmanuelChedal RobertKranjec HarriOlli MichaelUhrmann ManuelFettner KamilStoch DaikiIto SigurdPettersen NoriakiKasai SebastianColloredo PrimozPeterka JanMatura StephanHocke JakubJanda JonAaraas TakanobuOkabe StefanHula PrimozPikl
    C: AdamMalysz SimonAmmann GregorSchlierenzauer AndreasKüttel ThomasMorgenstern AndreasKofler MichaelUhrmann DimitryVassiliev MartinKoch WolfgangLoitzl AndersBardal MartinSchmitt DenisKornilov TomHilde JakubJanda JernejDamjan SigurdPettersen NoriakiKasai RobertKranjec HarriOlli KamilStoch PrimozPikl ManuelFettner SebastianColloredo MichaelNeumayer TakanobuOkabe JanMatura DaikiIto StefanHula StephanHocke EmmanuelChedal JonAaraas PrimozPeterka
    D: JakubJanda ThomasMorgenstern AndreasKüttel AndreasKofler MichaelUhrmann AdamMalysz WolfgangLoitzl TakanobuOkabe RobertKranjec SimonAmmann MartinKoch MichaelNeumayer JanMatura DimitryVassiliev DaikiIto NoriakiKasai JernejDamjan KamilStoch AndersBardal PrimozPeterka SigurdPettersen ManuelFettner HarriOlli SebastianColloredo MartinSchmitt DenisKornilov EmmanuelChedal StefanHula PrimozPikl StephanHocke TomHilde JonAaraas GregorSchlierenzauer

```python3 run.py example_ski_jumping.txt```

    Output:

    Parse input
         ... finished
    Problem statistics
      4 votes
      33 candidates
    Solve: build model
    Solve
    Coin0506I Presolve 66 (-2178) rows, 1089 (0) columns and 2178 (-2178) elements
    Clp0006I 0  Obj 0 Primal inf 65.999934 (66)
    Clp0006I 58  Obj 0.80073462 Primal inf 26.999978 (22)
    Clp0006I 88  Obj 0.96602388
    Clp0000I Optimal - objective value 0.96602388
    Coin0511I After Postsolve, objective 0.96602388, infeasibilities - dual 0 (0), primal 0 (0)
    Clp0032I Optimal objective 0.9660238751 - 88 iterations time 0.002, Presolve 0.00
    Postprocessing
        ... finished
    --------
    SOLUTION
      objective:  0.9660238751147842
      aggregation:
    ['DaikiIto' 'GregorSchlierenzauer' 'DenisKornilov' 'AndreasKüttel'
     'PrimozPeterka' 'MichaelNeumayer' 'EmmanuelChedal' 'StefanHula'
     'AndersBardal' 'MichaelUhrmann' 'KamilStoch' 'SimonAmmann' 'ManuelFettner'
     'TomHilde' 'NoriakiKasai' 'RobertKranjec' 'HarriOlli' 'JanMatura'
     'JernejDamjan' 'JakubJanda' 'MartinSchmitt' 'WolfgangLoitzl'
     'ThomasMorgenstern' 'MartinKoch' 'SebastianColloredo' 'PrimozPikl'
     'AndreasKofler' 'StephanHocke' 'TakanobuOkabe' 'SigurdPettersen'
     'AdamMalysz' 'JonAaraas' 'DimitryVassiliev']

# Interesting observation
When trying to solve instances with huge-candidate lists (warning: preprocessing implementation = slow; a few seconds), like **example_capital.txt**, something interesting happens in *Clp*:

    Clp0032I Optimal objective 0.7213888889 - 0 iterations time 2.262, Presolve 0.11, Idiot 2.14

- Clp uses most of the time in some routine called *Idiot*
  - *Very interesting theory!*
  - See [Crash-Starting the Simplex Method (Ivet Galabova, Julian Hall
); slides of 12/2017](http://ivetgalabova.com/assets/Crash-Starting-Simplex-Cuba.pdf)
