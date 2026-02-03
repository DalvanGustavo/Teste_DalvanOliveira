<template>
  <div style="max-width: 1100px; margin: 0 auto; padding: 16px;">
    <header style="display:flex; gap:16px; align-items:center; margin-bottom:16px;">
      <h2 style="margin:0;">ANS Despesas</h2>
      <nav style="display:flex; gap:12px;">
        <RouterLink to="/">Dashboard</RouterLink>
        <RouterLink to="/operadoras">Operadoras</RouterLink>
      </nav>
    </header>

    <RouterView />
  </div>
</template>
