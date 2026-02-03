import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import OperadorasList from "../views/OperadorasList.vue";
import OperadoraDetalhe from "../views/OperadoraDetalhe.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "dashboard", component: Dashboard },
    { path: "/operadoras", name: "operadoras", component: OperadorasList },
    { path: "/operadoras/:cnpj", name: "operadora", component: OperadoraDetalhe, props: true },
  ],
});
