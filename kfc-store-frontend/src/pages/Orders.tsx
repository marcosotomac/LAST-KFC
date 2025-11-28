import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { OrderCard, Order } from "@/components/OrderCard";
import { DndContext, DragEndEvent, closestCorners } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { Filter, Bell } from "lucide-react";
import { useNotifications } from "@/hooks/useNotifications";
import { Badge } from "@/components/ui/badge";

const mockOrders: Order[] = [
  {
    id: "ORD-001",
    customer: "Juan Pérez",
    items: [
      { name: "Bucket 8 pzas", quantity: 1 },
      { name: "Papas Grandes", quantity: 2 },
      { name: "Coca Cola 1L", quantity: 1 },
    ],
    total: 12.99,
    status: "pending",
    createdAt: new Date(Date.now() - 5 * 60000),
  },
  {
    id: "ORD-002",
    customer: "María García",
    items: [
      { name: "Zinger Sandwich", quantity: 1 },
      { name: "Papas Medianas", quantity: 1 },
    ],
    total: 8.99,
    status: "kitchen",
    createdAt: new Date(Date.now() - 12 * 60000),
  },
  {
    id: "ORD-003",
    customer: "Carlos Ruiz",
    items: [{ name: "Popcorn Chicken", quantity: 2 }],
    total: 6.5,
    status: "packing",
    createdAt: new Date(Date.now() - 8 * 60000),
  },
  {
    id: "ORD-004",
    customer: "Ana López",
    items: [
      { name: "Family Feast", quantity: 1 },
      { name: "Ensalada Cole Slaw", quantity: 2 },
    ],
    total: 24.99,
    status: "delivery",
    createdAt: new Date(Date.now() - 15 * 60000),
  },
];

const Orders = () => {
  const [orders, setOrders] = useState<Order[]>(mockOrders);
  const [filterStatus, setFilterStatus] = useState<Order["status"] | "all">("all");
  const { addNotification } = useNotifications();

  // Simulate new orders
  useEffect(() => {
    const interval = setInterval(() => {
      const shouldAddOrder = Math.random() > 0.7;
      if (shouldAddOrder) {
        const newOrder: Order = {
          id: `ORD-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
          customer: ["Pedro Martínez", "Laura Sánchez", "Diego Torres"][
            Math.floor(Math.random() * 3)
          ],
          items: [
            { name: "Bucket 8 pzas", quantity: 1 },
            { name: "Papas Medianas", quantity: 2 },
          ],
          total: Math.random() * 20 + 5,
          status: "pending",
          createdAt: new Date(),
        };
        setOrders((prev) => [newOrder, ...prev]);
        addNotification({
          title: "Nueva Orden",
          message: `Orden ${newOrder.id} de ${newOrder.customer}`,
          type: "order",
        });
      }
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, [addNotification]);

  // Check for slow orders
  useEffect(() => {
    const interval = setInterval(() => {
      orders.forEach((order) => {
        const minutesAgo = Math.floor(
          (Date.now() - order.createdAt.getTime()) / 60000
        );
        if (minutesAgo > 15 && order.status !== "delivery") {
          addNotification({
            title: "Orden Retrasada",
            message: `Orden ${order.id} lleva ${minutesAgo} minutos`,
            type: "alert",
          });
        }
      });
    }, 60000); // Every minute

    return () => clearInterval(interval);
  }, [orders, addNotification]);

  const handleStatusChange = (orderId: string, newStatus: Order["status"]) => {
    setOrders((prev) =>
      prev.map((order) =>
        order.id === orderId ? { ...order, status: newStatus } : order
      )
    );
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const activeOrder = orders.find((o) => o.id === active.id);
    if (!activeOrder) return;

    // Determine the new status based on the drop zone
    const newStatus = over.id as Order["status"];
    handleStatusChange(activeOrder.id, newStatus);
  };

  const filteredOrders = orders.filter(
    (order) => filterStatus === "all" || order.status === filterStatus
  );

  const getOrdersByStatus = (status: Order["status"]) =>
    orders.filter((order) => order.status === status);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Panel de Órdenes en Tiempo Real
          </h1>
          <p className="text-muted-foreground mt-2">
            Gestiona el flujo completo de pedidos con drag & drop
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="icon">
            <Bell className="w-4 h-4" />
          </Button>
          <Button>Nueva Orden</Button>
        </div>
      </div>

      <Tabs defaultValue="all" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="all" onClick={() => setFilterStatus("all")}>
            Todas
            <Badge variant="secondary" className="ml-2">
              {orders.length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="pending" onClick={() => setFilterStatus("pending")}>
            Pendientes
            <Badge variant="secondary" className="ml-2">
              {getOrdersByStatus("pending").length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="kitchen" onClick={() => setFilterStatus("kitchen")}>
            Cocina
            <Badge variant="secondary" className="ml-2">
              {getOrdersByStatus("kitchen").length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="packing" onClick={() => setFilterStatus("packing")}>
            Empaque
            <Badge variant="secondary" className="ml-2">
              {getOrdersByStatus("packing").length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="delivery" onClick={() => setFilterStatus("delivery")}>
            Delivery
            <Badge variant="secondary" className="ml-2">
              {getOrdersByStatus("delivery").length}
            </Badge>
          </TabsTrigger>
        </TabsList>

        <DndContext collisionDetection={closestCorners} onDragEnd={handleDragEnd}>
          <TabsContent value="all" className="space-y-4">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              <SortableContext
                items={filteredOrders.map((o) => o.id)}
                strategy={verticalListSortingStrategy}
              >
                {filteredOrders.map((order) => (
                  <OrderCard
                    key={order.id}
                    order={order}
                    onStatusChange={handleStatusChange}
                  />
                ))}
              </SortableContext>
            </div>
          </TabsContent>

          {["pending", "kitchen", "packing", "delivery"].map((status) => (
            <TabsContent key={status} value={status} className="space-y-4">
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                <SortableContext
                  items={getOrdersByStatus(status as Order["status"]).map((o) => o.id)}
                  strategy={verticalListSortingStrategy}
                >
                  {getOrdersByStatus(status as Order["status"]).map((order) => (
                    <OrderCard
                      key={order.id}
                      order={order}
                      onStatusChange={handleStatusChange}
                    />
                  ))}
                </SortableContext>
              </div>
            </TabsContent>
          ))}
        </DndContext>
      </Tabs>
    </div>
  );
};

export default Orders;
