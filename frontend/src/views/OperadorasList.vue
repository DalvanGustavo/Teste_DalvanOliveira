<template>
  <div>
    <h3>Operadoras</h3>

    <div style="display:flex; gap:8px; margin-bottom:12px;">
      <input
        v-model="search"
        placeholder="Buscar por Razão Social ou CNPJ"
        style="flex:1; padding:8px;"
        @keyup.enter="applySearch"
      />
      <button @click="applySearch">Buscar</button>
      <button @click="clearSearch" :disabled="!search">Limpar</button>
    </div>

    <Loading v-if="loading" />
    <ErrorBox v-else-if="error" :message="error" />

    <div v-else>
      <p v-if="total === 0">Nenhuma operadora encontrada.</p>

      <table v-else border="1" cellpadding="8" cellspacing="0" style="width:100%; border-collapse:collapse;">
        <thead>
          <tr>
            <th>CNPJ</th>
            <th>Razão Social</th>
            <th>UF</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in rows" :key="o.cnpj">
            <td>{{ o.cnpj }}</td>
            <td>{{ o.razao_social }}</td>
            <td>{{ o.uf || "-" }}</td>
            <td>
              <RouterLink :to="`/operadoras/${o.cnpj}`">Detalhes</RouterLink>
            </td>
          </tr>
        </tbody>
      </table>

      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
        <div>
          Página {{ page }} de {{ totalPages }} — Total: {{ total }}
        </div>

        <div style="display:flex; gap:8px;">
          <button @click="prev" :disabled="page <= 1">Anterior</button>
          <button @click="next" :disabled="page >= totalPages">Próxima</button>

          <select v-model.number="limit" @change="changeLimit">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { api } from "../api/client";
import Loading from "../components/Loading.vue";
import ErrorBox from "../components/ErrorBox.vue";

const loading = ref(true);
const error = ref("");
const rows = ref([]);
const total = ref(0);

const page = ref(1);
const limit = ref(10);

const search = ref("");
const appliedSearch = ref("");

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / limit.value)));

async function fetchData() {
  loading.value = true;
  error.value = "";
  try {
    const params = { page: page.value, limit: limit.value };
    if (appliedSearch.value) params.search = appliedSearch.value;

    const { data } = await api.get("/api/operadoras", { params });
    rows.value = data.data;
    total.value = data.total;
  } catch (e) {
    error.value = e?.response?.data?.detail || "Falha ao carregar operadoras.";
  } finally {
    loading.value = false;
  }
}

function applySearch() {
  appliedSearch.value = search.value.trim();
  page.value = 1;
  fetchData();
}

function clearSearch() {
  search.value = "";
  appliedSearch.value = "";
  page.value = 1;
  fetchData();
}

function prev() {
  if (page.value > 1) {
    page.value--;
    fetchData();
  }
}

function next() {
  if (page.value < totalPages.value) {
    page.value++;
    fetchData();
  }
}

function changeLimit() {
  page.value = 1;
  fetchData();
}

onMounted(fetchData);
</script>
