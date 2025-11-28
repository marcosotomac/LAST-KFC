import { NavLink } from "./NavLink";
import { LayoutDashboard, ShoppingCart, Package, UtensilsCrossed, Menu, Users } from "lucide-react";
import { Button } from "./ui/button";
import { Sheet, SheetContent, SheetTrigger } from "./ui/sheet";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/orders", icon: ShoppingCart, label: "Pedidos" },
  { to: "/inventory", icon: Package, label: "Inventario" },
  { to: "/menu", icon: UtensilsCrossed, label: "Menú" },
  { to: "/staff", icon: Users, label: "Staff" },
];

export const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <aside className="hidden md:fixed md:inset-y-0 md:flex md:w-64 md:flex-col">
        <div className="flex flex-col flex-grow border-r border-border bg-card overflow-y-auto">
          <div className="flex items-center justify-center h-16 px-4 border-b border-border bg-primary">
            <h1 className="text-2xl font-bold text-primary-foreground">KFC Manager</h1>
          </div>
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className="flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors hover:bg-accent hover:text-accent-foreground"
                activeClassName="bg-accent text-accent-foreground"
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </aside>

      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 flex items-center justify-between h-16 px-4 border-b border-border bg-card">
        <h1 className="text-xl font-bold text-primary">KFC Manager</h1>
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon">
              <Menu className="h-6 w-6" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64 p-0">
            <div className="flex items-center justify-center h-16 px-4 border-b border-border bg-primary">
              <h1 className="text-xl font-bold text-primary-foreground">KFC Manager</h1>
            </div>
            <nav className="px-4 py-6 space-y-2">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className="flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors hover:bg-accent hover:text-accent-foreground"
                  activeClassName="bg-accent text-accent-foreground"
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </SheetContent>
        </Sheet>
      </div>

      {/* Main Content */}
      <div className="md:pl-64 pt-16 md:pt-0">
        <main className="p-6 md:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};
