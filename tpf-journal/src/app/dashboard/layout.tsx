import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />

      <SidebarTrigger />
      <div className="!py-[2vh] !px-[1vw] w-[90vw] h-[100vh] ">{children}</div>
    </SidebarProvider>
  );
}
