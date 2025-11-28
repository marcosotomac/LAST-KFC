import { Card } from "@/components/ui/card";
import { TrendingUp, ShoppingCart, Users, DollarSign, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const stats = [
  {
    title: "Ventas Hoy",
    value: "$1,234.56",
    change: "+12.5%",
    icon: DollarSign,
    color: "text-green-600",
  },
  {
    title: "Órdenes Activas",
    value: "23",
    change: "8 pendientes",
    icon: ShoppingCart,
    color: "text-orange-600",
  },
  {
    title: "Clientes Atendidos",
    value: "156",
    change: "+8.2%",
    icon: Users,
    color: "text-purple-600",
  },
  {
    title: "Tiempo Promedio",
    value: "12 min",
    change: "-2 min vs ayer",
    icon: Clock,
    color: "text-blue-600",
  },
];

const salesByHour = [
  { hour: "9am", ventas: 45 },
  { hour: "10am", ventas: 78 },
  { hour: "11am", ventas: 120 },
  { hour: "12pm", ventas: 189 },
  { hour: "1pm", ventas: 234 },
  { hour: "2pm", ventas: 198 },
  { hour: "3pm", ventas: 156 },
  { hour: "4pm", ventas: 145 },
  { hour: "5pm", ventas: 178 },
  { hour: "6pm", ventas: 210 },
];

const topProducts = [
  { name: "Bucket 8 pzas", sales: 45, revenue: 719.55 },
  { name: "Zinger Sandwich", sales: 38, revenue: 227.62 },
  { name: "Papas Grandes", sales: 56, revenue: 167.44 },
  { name: "Popcorn Chicken", sales: 29, revenue: 130.21 },
  { name: "Ensalada", sales: 22, revenue: 43.78 },
];

const recentOrders = [
  {
    id: "#1234",
    customer: "Juan Pérez",
    items: 3,
    total: "$12.99",
    status: "completed",
  },
  {
    id: "#1235",
    customer: "María García",
    items: 2,
    total: "$8.99",
    status: "pending",
  },
  {
    id: "#1236",
    customer: "Carlos Ruiz",
    items: 1,
    total: "$6.50",
    status: "preparing",
  },
  {
    id: "#1237",
    customer: "Ana López",
    items: 5,
    total: "$24.99",
    status: "completed",
  },
  {
    id: "#1238",
    customer: "Luis Torres",
    items: 2,
    total: "$11.49",
    status: "preparing",
  },
];

const Dashboard = () => {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Vista general del negocio en tiempo real
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title} className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">
                    {stat.title}
                  </p>
                  <p className="text-3xl font-bold">{stat.value}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {stat.change}
                  </p>
                </div>
                <Icon className={`w-12 h-12 ${stat.color} opacity-80`} />
              </div>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <h2 className="text-xl font-bold mb-6">Ventas por Hora</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={salesByHour}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="ventas"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-bold mb-6">Productos Más Vendidos</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topProducts}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="sales" fill="hsl(var(--primary))" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-bold mb-6">Pedidos Recientes</h2>
        <div className="space-y-4">
          {recentOrders.map((order) => (
            <div
              key={order.id}
              className="flex items-center justify-between p-4 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
            >
              <div className="flex items-center gap-4">
                <div>
                  <p className="font-semibold">{order.id}</p>
                  <p className="text-sm text-muted-foreground">
                    {order.customer}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <p className="text-sm text-muted-foreground">
                  {order.items} items
                </p>
                <p className="font-bold text-primary">{order.total}</p>
                <Badge
                  variant={
                    order.status === "completed" ? "default" : "secondary"
                  }
                  className={
                    order.status === "completed"
                      ? "bg-green-500/20 text-green-700 dark:text-green-400"
                      : order.status === "preparing"
                        ? "bg-orange-500/20 text-orange-700 dark:text-orange-400"
                        : "bg-yellow-500/20 text-yellow-700 dark:text-yellow-400"
                  }
                >
                  {order.status === "completed"
                    ? "Completado"
                    : order.status === "preparing"
                      ? "Preparando"
                      : "Pendiente"}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default Dashboard;
