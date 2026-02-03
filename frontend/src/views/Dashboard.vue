<template>
  <div>
    <h3>Dashboard</h3>

    <Loading v-if="loading" />
    <ErrorBox v-else-if="error" :message="error" />

    <div v-else>
      <p><strong>Total despesas:</strong> {{ formatBR(stats.total_despesas) }}</p>
      <p><strong>Média:</strong> {{ formatBR(stats.media_despesas) }}</p>

      <h4>Distribuição por UF</h4>
      <canvas ref="ufCanvas" height="120"></canvas>

      <h4 style="margin-top:16px;">Top 5 operadoras</h4>
      <ol>
        <li v-for="o in stats.top5_operadoras" :key="o.cnpj">
          {{ o.razao_social }} — {{ formatBR(o.total) }}
        </li>
      </ol>
    </div>
  </div>
</template>

<script setup>
import { nextTick } from "vue";
import { onMounted, ref } from "vue";
import { api } from "../api/client";
import Loading from "../components/Loading.vue";
import ErrorBox from "../components/ErrorBox.vue";
import { Chart } from "chart.js/auto";

const loading = ref(true);
const error = ref("");
const stats = ref(null);

const ufCanvas = ref(null);
let chartInstance = null;

function formatBR(v) {
  const n = Number(v || 0);
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

async function loadStats() {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await api.get("/api/estatisticas");
    stats.value = data;
    loading.value = false;
    await nextTick();
    const labels = data.despesas_por_uf.map(x => x.uf);
    const values = data.despesas_por_uf.map(x => Number(x.total));

    if (chartInstance) chartInstance.destroy();
    chartInstance = new Chart(ufCanvas.value, {
      type: "bar",
      data: {
        labels,
        datasets: [{ label: "Total de despesas", data: values }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: true } },
      },
    });
  } catch (e) {
    error.value = e?.response?.data?.detail || "Falha ao carregar estatísticas.";
  } finally {
    loading.value = false;
  }
}
console.log("canvas:", ufCanvas.value);

onMounted(loadStats);
</script>
