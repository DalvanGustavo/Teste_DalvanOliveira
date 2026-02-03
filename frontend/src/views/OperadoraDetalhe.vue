<template>
  <div>
    <h3>Detalhe da operadora</h3>
    <p><RouterLink to="/operadoras">← Voltar</RouterLink></p>

    <Loading v-if="loading" />
    <ErrorBox v-else-if="error" :message="error" />

    <div v-else>
      <h4 style="margin-bottom:6px;">{{ operadora.razao_social }}</h4>
      <p><strong>CNPJ:</strong> {{ operadora.cnpj }}</p>
      <p><strong>UF:</strong> {{ operadora.uf || "-" }}</p>
      <p><strong>Registro ANS:</strong> {{ operadora.registro_ans ?? "-" }}</p>

      <h4 style="margin-top:16px;">Histórico de despesas</h4>
      <p v-if="despesas.length === 0">Sem despesas registradas para esta operadora.</p>
      <canvas v-else ref="lineCanvas" height="120"></canvas>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { api } from "../api/client";
import Loading from "../components/Loading.vue";
import ErrorBox from "../components/ErrorBox.vue";
import { Chart } from "chart.js/auto";

const props = defineProps({ cnpj: { type: String, required: true } });

const loading = ref(true);
const error = ref("");

const operadora = ref(null);
const despesas = ref([]);

const lineCanvas = ref(null);
let chartInstance = null;

function formatBR(v) {
  const n = Number(v || 0);
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

async function loadAll() {
  loading.value = true;
  error.value = "";
  try {
    const [opRes, despRes] = await Promise.all([
      api.get(`/api/operadoras/${props.cnpj}`),
      api.get(`/api/operadoras/${props.cnpj}/despesas`),
    ]);

    operadora.value = opRes.data;
    despesas.value = despRes.data;

    if (despesas.value.length > 0) {
      const labels = despesas.value.map(d => `${d.ano}T${d.trimestre}`);
      const values = despesas.value.map(d => Number(d.valor_despesas));

      if (chartInstance) chartInstance.destroy();
      chartInstance = new Chart(lineCanvas.value, {
        type: "line",
        data: {
          labels,
          datasets: [{ label: "Despesas", data: values }],
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.dataset.label}: ${formatBR(ctx.raw)}`,
              },
            },
          },
        },
      });
    }
  } catch (e) {
    const status = e?.response?.status;
    if (status === 404) error.value = "Operadora não encontrada.";
    else error.value = e?.response?.data?.detail || "Falha ao carregar detalhes.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadAll);
</script>
