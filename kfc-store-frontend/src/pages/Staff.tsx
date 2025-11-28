import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { UserPlus, Search, Edit, Trash2 } from "lucide-react";
import { toast } from "sonner";

interface StaffMember {
  id: string;
  name: string;
  email: string;
  role: "admin" | "cashier" | "cook" | "packer" | "delivery";
  status: "active" | "inactive";
  lastActive: string;
}

const mockStaff: StaffMember[] = [
  {
    id: "1",
    name: "Admin Principal",
    email: "admin@kfc.com",
    role: "admin",
    status: "active",
    lastActive: "Ahora",
  },
  {
    id: "2",
    name: "Carlos Rodríguez",
    email: "carlos@kfc.com",
    role: "cashier",
    status: "active",
    lastActive: "Hace 5 min",
  },
  {
    id: "3",
    name: "María González",
    email: "maria@kfc.com",
    role: "cook",
    status: "active",
    lastActive: "Hace 2 min",
  },
];

const roleLabels = {
  admin: "Administrador",
  cashier: "Cajero",
  cook: "Cocinero",
  packer: "Empacador",
  delivery: "Delivery",
};

const roleColors = {
  admin: "bg-purple-500/20 text-purple-700 dark:text-purple-400",
  cashier: "bg-blue-500/20 text-blue-700 dark:text-blue-400",
  cook: "bg-orange-500/20 text-orange-700 dark:text-orange-400",
  packer: "bg-green-500/20 text-green-700 dark:text-green-400",
  delivery: "bg-yellow-500/20 text-yellow-700 dark:text-yellow-400",
};

const Staff = () => {
  const [staff, setStaff] = useState<StaffMember[]>(mockStaff);
  const [searchTerm, setSearchTerm] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState<StaffMember | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    role: "cashier" as StaffMember["role"],
  });

  const filteredStaff = staff.filter(
    (member) =>
      member.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleOpenDialog = (member?: StaffMember) => {
    if (member) {
      setEditingStaff(member);
      setFormData({
        name: member.name,
        email: member.email,
        role: member.role,
      });
    } else {
      setEditingStaff(null);
      setFormData({ name: "", email: "", role: "cashier" });
    }
    setDialogOpen(true);
  };

  const handleSave = () => {
    if (editingStaff) {
      setStaff(
        staff.map((m) =>
          m.id === editingStaff.id
            ? { ...m, ...formData }
            : m
        )
      );
      toast.success("Usuario actualizado correctamente");
    } else {
      const newMember: StaffMember = {
        id: Math.random().toString(36).substr(2, 9),
        ...formData,
        status: "active",
        lastActive: "Ahora",
      };
      setStaff([...staff, newMember]);
      toast.success("Usuario registrado correctamente");
    }
    setDialogOpen(false);
  };

  const handleDelete = (id: string) => {
    setStaff(staff.filter((m) => m.id !== id));
    toast.success("Usuario eliminado");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestión de Staff</h1>
          <p className="text-muted-foreground mt-2">
            Administra el personal del restaurante
          </p>
        </div>
        <Button onClick={() => handleOpenDialog()}>
          <UserPlus className="w-4 h-4 mr-2" />
          Registrar Usuario
        </Button>
      </div>

      <Card className="p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por nombre o email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nombre</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Rol</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead>Última Actividad</TableHead>
              <TableHead className="text-right">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredStaff.map((member) => (
              <TableRow key={member.id}>
                <TableCell className="font-medium">{member.name}</TableCell>
                <TableCell>{member.email}</TableCell>
                <TableCell>
                  <Badge className={roleColors[member.role]}>
                    {roleLabels[member.role]}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge
                    variant={member.status === "active" ? "default" : "secondary"}
                  >
                    {member.status === "active" ? "Activo" : "Inactivo"}
                  </Badge>
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {member.lastActive}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleOpenDialog(member)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(member.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingStaff ? "Editar Usuario" : "Registrar Nuevo Usuario"}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Nombre Completo</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
              />
            </div>
            <div>
              <Label htmlFor="role">Rol</Label>
              <Select
                value={formData.role}
                onValueChange={(value) =>
                  setFormData({ ...formData, role: value as StaffMember["role"] })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(roleLabels).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSave}>Guardar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Staff;
