# apbase.config

Configurações do processo inteiro usadas pelo pipeline de mapas.

:::{py:data} apbase.config

Configurações globais consultadas quando uma classe é criada sem um valor explícito.

**Exemplos**

```pycon
>>> import apbase
>>> from apbase.kriging import Kriging
>>> apbase.config["n_threads"] = 4
>>> Kriging().n_threads
4
```

Objeto de configuração global. A configuração mais usada é `apbase.config["n_threads"]`.

:::
