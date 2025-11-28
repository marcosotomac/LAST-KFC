import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { AlertTriangle, Package } from "lucide-react";

const inventory = [
  { name: "Pollo Fresco", quantity: 45, unit: "kg", min: 30, max: 100, status: "good" },
  { name: "Papas", quantity: 12, unit: "kg", min: 20, max: 80, status: "low" },
  { name: "Aceite de Fritura", quantity: 8, unit: "L", min: 15, max: 50, status: "low" },
  { name: "Pan para Sandwiches", quantity: 89, unit: "unidades", min: 40, max: 150, status: "good" },
  { name: "Lechuga", quantity: 5, unit: "kg", min: 10, max: 30, status: "critical" },
  { name: "Tomate", quantity: 18, unit: "kg", min: 8, max: 35, status: "good" },
  { name: "Bebidas (Coca Cola)", quantity: 42, unit: "unidades", min: 30, max: 100, status: "good" },
  { name: "Salsa BBQ", quantity: 6, unit: "L", min: 10, max: 40, status: "low" },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "critical":
      return "bg-destructive text-destructive-foreground";
    case "low":
      return "bg-warning text-warning-foreground";
    default:
      return "bg-success text-success-foreground";
  }
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case "critical":
      return "Crítico";
    case "low":
      return "Bajo";
    default:
      return "Óptimo";
  }
};

const Inventory = () => {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Control de Inventario</h1>
          <p className="text-muted-foreground mt-2">Monitorea el stock de productos</p>
        </div>
        <Button className="bg-primary hover:bg-primary/90">
          Agregar Producto
        </Button>
      </div>

      {/* Alert for low stock */}
      <Card className="p-4 border-warning bg-warning/5">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-warning" />
          <div>
            <p className="font-medium">Alerta de Inventario</p>
            <p className="text-sm text-muted-foreground">
              3 productos están por debajo del nivel mínimo
            </p>
          </div>
        </div>
      </Card>

      {/* Inventory Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {inventory.map((item) => {
          const percentage = (item.quantity / item.max) * 100;
          
          return (
            <Card key={item.name} className="p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-secondary">
                    <Package className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-bold">{item.name}</h3>
                    <p className="text-sm text-muted-foreground">{item.unit}</p>
                  </div>
                </div>
                <Badge className={getStatusColor(item.status)}>
                  {getStatusLabel(item.status)}
                </Badge>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Cantidad</span>
                  <span className="font-bold text-lg">
                    {item.quantity} {item.unit}
                  </span>
                </div>
                <Progress value={percentage} className="h-2" />
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Mín: {item.min}</span>
                  <span>Máx: {item.max}</span>
                </div>
              </div>

              <div className="flex gap-2 mt-4">
                <Button variant="outline" size="sm" className="flex-1">
                  Ajustar
                </Button>
                <Button size="sm" className="flex-1 bg-primary hover:bg-primary/90">
                  Reabastecer
                </Button>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default Inventory;
