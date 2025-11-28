import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Star, Edit, Plus, Trash2, Search } from "lucide-react";
import { ProductDialog, Product } from "@/components/ProductDialog";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

const mockProducts: Product[] = [
  {
    id: "1",
    name: "Bucket Original 8 Piezas",
    description: "8 piezas de pollo frito original con nuestra receta secreta",
    price: 15.99,
    category: "Pollo Frito",
    available: true,
  },
  {
    id: "2",
    name: "Zinger Sandwich",
    description: "Sándwich picante con filete de pollo crujiente",
    price: 5.99,
    category: "Sandwiches",
    available: true,
  },
  {
    id: "3",
    name: "Papas Fritas Grandes",
    description: "Papas fritas crujientes tamaño grande",
    price: 2.99,
    category: "Complementos",
    available: true,
  },
  {
    id: "4",
    name: "Ensalada Cole Slaw",
    description: "Ensalada fresca de repollo y zanahoria",
    price: 1.99,
    category: "Ensaladas",
    available: true,
  },
  {
    id: "5",
    name: "Popcorn Chicken",
    description: "Bocaditos de pollo crujiente",
    price: 4.49,
    category: "Pollo Frito",
    available: true,
  },
  {
    id: "6",
    name: "Coca Cola 1L",
    description: "Bebida gaseosa de 1 litro",
    price: 2.49,
    category: "Bebidas",
    available: false,
  },
];

const categories = [
  "Todos",
  "Pollo Frito",
  "Hamburguesas",
  "Sandwiches",
  "Ensaladas",
  "Complementos",
  "Bebidas",
  "Postres",
];

const Menu = () => {
  const [products, setProducts] = useState<Product[]>(mockProducts);
  const [selectedCategory, setSelectedCategory] = useState("Todos");
  const [searchTerm, setSearchTerm] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | undefined>();
  const [showOnlyAvailable, setShowOnlyAvailable] = useState(false);

  const filteredProducts = products.filter((product) => {
    const matchesCategory =
      selectedCategory === "Todos" || product.category === selectedCategory;
    const matchesSearch = product.name
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesAvailability = !showOnlyAvailable || product.available;
    return matchesCategory && matchesSearch && matchesAvailability;
  });

  const handleSaveProduct = (productData: Omit<Product, "id"> & { id?: string }) => {
    if (productData.id) {
      setProducts(
        products.map((p) =>
          p.id === productData.id ? { ...productData, id: productData.id } : p
        )
      );
      toast.success("Producto actualizado correctamente");
    } else {
      const newProduct: Product = {
        ...productData,
        id: Math.random().toString(36).substr(2, 9),
      };
      setProducts([...products, newProduct]);
      toast.success("Producto creado correctamente");
    }
    setEditingProduct(undefined);
  };

  const handleDeleteProduct = (id: string) => {
    setProducts(products.filter((p) => p.id !== id));
    toast.success("Producto eliminado");
  };

  const handleOpenDialog = (product?: Product) => {
    setEditingProduct(product);
    setDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestión de Menú</h1>
          <p className="text-muted-foreground mt-2">
            CRUD completo de productos del menú
          </p>
        </div>
        <Button onClick={() => handleOpenDialog()}>
          <Plus className="w-4 h-4 mr-2" />
          Agregar Producto
        </Button>
      </div>

      <Card className="p-6">
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar productos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="available-only"
              checked={showOnlyAvailable}
              onCheckedChange={setShowOnlyAvailable}
            />
            <Label htmlFor="available-only">Solo disponibles</Label>
          </div>
        </div>

        <div className="flex gap-2 flex-wrap mb-6">
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? "default" : "outline"}
              className="rounded-full"
              onClick={() => setSelectedCategory(category)}
            >
              {category}
            </Button>
          ))}
        </div>
      </Card>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredProducts.map((product) => (
          <Card
            key={product.id}
            className="overflow-hidden hover:shadow-lg transition-shadow"
          >
            <div className="aspect-video bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
              {product.image ? (
                <img
                  src={product.image}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-4xl">🍗</span>
              )}
            </div>
            <div className="p-6">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-bold text-lg">{product.name}</h3>
                <Badge
                  variant={product.available ? "default" : "secondary"}
                  className={
                    product.available
                      ? "bg-green-500/20 text-green-700 dark:text-green-400"
                      : ""
                  }
                >
                  {product.available ? "Disponible" : "No disponible"}
                </Badge>
              </div>

              <Badge variant="outline" className="mb-3">
                {product.category}
              </Badge>

              <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                {product.description}
              </p>

              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-primary">
                  ${product.price.toFixed(2)}
                </span>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleOpenDialog(product)}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDeleteProduct(product.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <Card className="p-12 text-center">
          <p className="text-muted-foreground">
            No se encontraron productos con los filtros seleccionados
          </p>
        </Card>
      )}

      <ProductDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        product={editingProduct}
        onSave={handleSaveProduct}
      />
    </div>
  );
};

export default Menu;
