<template>
  <div class="container">
    <header class="header">
      <div class="brand">
        <h2>ANS Despesas</h2>
        <small>Dashboard e consulta de operadoras</small>
      </div>

      <nav class="nav">
        <RouterLink to="/">Dashboard</RouterLink>
        <RouterLink to="/operadoras">Operadoras</RouterLink>
      </nav>
    </header>

    <RouterView />
  </div>
</template>