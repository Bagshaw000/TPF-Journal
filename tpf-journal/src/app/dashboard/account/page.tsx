"use client";
import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import Image from "next/image";
import mount from "../../../../public/mount.svg";
import ctrader from "../../../../public/ctrader.jpg";
import mt5 from "../../../../public/mt5.jpg";
import { ChartNoAxesCombined, CirclePlus } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@radix-ui/react-label";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useUser } from "@supabase/auth-helpers-react";
import client from "@/api/client";
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
  Form,
} from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

export default  function Page() {

  const [formValues, setFormValues] = useState({
    strategyName: "",
    entryLogic: "",
    exitLogic: "",
    tpLogic: "",
    slLogic: "",
    tradeManagement: "",
    session: "",
    riskProfile: "",
    status: "",
  });

  const [accValues, setAccountValues] = useState({
    
  })

  const handleChange = (field: string, value: string) => {
    setFormValues((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log(formValues)
    const user_id = (await client.auth.getUser()).data.user?.id;

    const strategyObj = {
      name: formValues.strategyName,
      entry_logic: formValues.entryLogic,
      exit_logic: formValues.exitLogic,
      strategy_session:formValues.session || null,
      status: formValues.status || null,
      takeprofit_logic: formValues.tpLogic,
      trade_management: formValues.tradeManagement,
      risk_profile: formValues.riskProfile || null,
      user_id: user_id
    }
     
    const uploadStrategy = (await client.from("strategy").insert([strategyObj]))


//     if (uploadStrategy.status === 201){
//  setDialogOpen(false); 
//     }
    


    


   
    // Save to page state or send to API
  };


  const [pageState, setPageState] = useState(true);
  const handlePageToggle = (element: boolean) => {
    setPageState(element);
  };
 
  const [userAccs, setUserAccs] = useState<null | Array<any>>([]);
  const [userStrategy, setUserStrategy] = useState<null | Array<any>>([]);

  // console.log(data)
  useEffect(() => {
    const fetchUserAccount = async () => {
   const user_id = (await client.auth.getUser()).data.user?.id;
      const acc = await client
        .from("accounts")
        .select("*")
        .eq("user_id", user_id);

      const strategy = await client
        .from("strategy")
        .select("*")
        .eq("user_id", user_id);

      setUserAccs(acc.data);
      setUserStrategy(strategy.data);

      
    };

    fetchUserAccount();
  }, []);

  return (
    <div className="mt-auto w-full h-full">
      {/* The Header Toggle */}
      <div className="w-[100%]  !mx-auto  border-b-2 !my-[50px]">
        <div className="flex flex-row justify-between items-end !mb-[5px]">
          <div className="!mb-[10px] flex flex-row">
            <button
              className="!mr-[20px] "
              onClick={() => handlePageToggle(true)}
            >
              Account
              {pageState ? (
                <hr className="border-spacing-1.5 bg-blue-500" />
              ) : (
                <hr className="hidden" />
              )}
            </button>
            <button onClick={() => handlePageToggle(false)}>
              Strategy
              {!pageState ? (
                <hr className="border-1.5 bg-blue-500" />
              ) : (
                <hr className="hidden" />
              )}
            </button>
          </div>
          {}
          {pageState ? (
            // Account Page button
            <div className="w-fit !ml-[10px] !my-auto text-lg flex flex-row justify-between items-center font-light">
              <Dialog>
                <form>
                  <DialogTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      className="!mr-[10px] !py-[16px] !px-[12px] text-neutral-400"
                    >
                      <CirclePlus />{" "}
                      <span className="font-light text-base">
                        Connect new account
                      </span>
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px] !p-[20px] text-xl">
                    <DialogHeader>
                      <DialogTitle className="text-2xl">Connect a new trading account</DialogTitle>
                      <DialogDescription></DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4">
                      <div className="grid gap-3">
                        <Label htmlFor="name-1">Account Id</Label>
                        <Input
                          id="accId"
                          name="accId"
                          placeholder="1234567"
                          defaultValue="1234567"
                          className="!p-[10px]"
                          // required
                        />
                      </div>
                      <div className="grid gap-3">
                        <Label htmlFor="server">Server</Label>
                        <Input
                          id="server"
                          name="server"
                          defaultValue="Demo-Example-sc"
                          className="!p-[10px]"
                        />
                      </div>
                      <div className="grid gap-3">
                        <Label htmlFor="password">Password</Label>
                        <Input
                          id="password"
                          name="password"
                          defaultValue="****"
                          className="!p-[10px]"
                          type="password"
                        />
                      </div>

                      <div className="grid gap-3">
                        <Label htmlFor="deposit">Initial Deposit</Label>
                        <Input
                          id="deposit"
                          name="deposit"
                          defaultValue="0.00"
                          placeholder="5000.00"
                          className="!p-[10px]"
                          type="number"
                        />
                      </div>
                      <div className="grid gap-3">
                        <Label htmlFor="year">Account age in years</Label>
                        <Input
                          id="year"
                          name="year"
                          defaultValue="@peduarte"
                          className="!p-[10px]"
                          type="number"
                          placeholder="3"
                        />
                      </div>

                      <div className="grid gap-3">
                        <Label htmlFor="username-1">Choose platform</Label>
                        <Select>
                          <SelectTrigger className="w-fit !px-[10px]">
                            <SelectValue placeholder="Select platform" />
                          </SelectTrigger>
                          <SelectContent className="w-fit h-fit gap-1 ">
                            <SelectGroup>
                              <SelectLabel>Trading Platform</SelectLabel>
                              <SelectItem value="mt5">Meta Trader 5</SelectItem>
                              <SelectItem value="c-trader">C-Trader</SelectItem>
                              <SelectItem value="m-trader">
                                Match Trader
                              </SelectItem>
                            </SelectGroup>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <DialogFooter>
                      {/* <DialogClose asChild>
                        <Button variant="outline" className="!p-1">
                          Cancel
                        </Button>
                      </DialogClose> */}
                      <Button type="submit" className="!p-5 text-base" >
                        Connect
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </form>
              </Dialog>
              {/* Platform */}
              <Select>
                <SelectTrigger className="w-fit !px-[10px] text-base">
                  <SelectValue placeholder="Filter by platform"  />
                </SelectTrigger>
                <SelectContent className="w-fit h-fit gap-1 ">
                  <SelectGroup>
                    <SelectLabel>Trading Platform</SelectLabel>
                    <SelectItem value="mt5">Meta Trader 5</SelectItem>
                    <SelectItem value="c-trader">C-Trader</SelectItem>
                    <SelectItem value="m-trader">Match Trader</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
          ) : (
            <>
              {/* Strategy connect button */}

              <Dialog>
                <DialogTrigger>
                  <Button
                    variant="outline"
                    size="sm"
                    className="!mr-[10px] !py-[16px] !px-[12px] text-neutral-400"
                  >
                    <CirclePlus />{" "}
                    <span className="font-light text-sm"> Add Strategy</span>
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[600px] !p-[20px]">
                  <DialogHeader>
                    <DialogTitle> Define Strategy</DialogTitle>
                    <DialogDescription></DialogDescription>
                  </DialogHeader>

                  <form onSubmit={handleSubmit} className="grid gap-4">
                    {/* Strategy Name */}
                    <div>
                      <label>Name</label>
                      <Input
                        value={formValues.strategyName}
                        onChange={(e) =>
                          handleChange("strategyName", e.target.value)
                        }
                        placeholder="Enter strategy name"
                        required
                      />
                    </div>

                    {/* Entry Logic */}
                    <div>
                      <label>Entry Logic</label>
                      <Textarea
                        value={formValues.entryLogic}
                        onChange={(e) =>
                          handleChange("entryLogic", e.target.value)
                        }
                        placeholder="Enter entry logic"
                        required
                      />
                    </div>

                    {/* Exit Logic */}
                    <div>
                      <label>Exit Logic</label>
                      <Textarea
                        value={formValues.exitLogic}
                        onChange={(e) =>
                          handleChange("exitLogic", e.target.value)
                        }
                        placeholder="Enter exit logic"
                        required
                      />
                    </div>

                    {/* Take Profit */}
                    <div>
                      <label>Take Profit</label>
                      <Textarea
                        value={formValues.tpLogic}
                        onChange={(e) =>
                          handleChange("tpLogic", e.target.value)
                        }
                        placeholder="Enter take profit logic"
                        required
                      />
                    </div>

                    {/* Trade Management */}
                    <div>
                      <label>Trade Management</label>
                      <Textarea
                        value={formValues.tradeManagement}
                        onChange={(e) =>
                          handleChange("tradeManagement", e.target.value)
                        }
                        placeholder="Enter trade management"
                        required
                      />
                    </div>

                    {/* Session */}
                    <div>
                      <label>Session</label>
                      <Select
                        value={formValues.session}
                        onValueChange={(val) => handleChange("session", val)}
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select session" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Asian">Asian</SelectItem>
                          <SelectItem value="London">London</SelectItem>
                          <SelectItem value="New York">New York</SelectItem>
                          <SelectItem value="Sydney">Sydney</SelectItem>
                          <SelectItem value="None">None</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Risk Profile */}
                    <div>
                      <label>Risk Profile</label>
                      <Select
                        value={formValues.riskProfile}
                        onValueChange={(val) =>
                          handleChange("riskProfile", val)
                        }
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select risk profile" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="high">High</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="low">Low</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Status */}
                    <div>
                      <label>Status</label>
                      <Select
                        value={formValues.status}
                        onValueChange={(val) => handleChange("status", val)}
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Active">Active</SelectItem>
                          <SelectItem value="Testing">Testing</SelectItem>
                          <SelectItem value="Retired">Retired</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Submit Button */}
                    <Button type="submit" className="!p-5">
                      Add Strategy
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
              {/* </Form> */}
            </>
          )}
        </div>
      </div>

      {/* List all user trading account linked */}
      {pageState ? (
        // Account page
        <div className="w-[100%] !mt-[50px] flex flex-row justify-between">
          {userAccs ? (
            userAccs!.map((element) => (
              <Link
                href={{
                  pathname: "/dashboard/account/statistics",
                  query: { id: element.id },
                }}
                className="h-fit w-[30%] bg-neutral-900 rounded-2xl !mb-[20px] !my-auto flex flex-row justify-between items-center !px-7 !py-7 font-light text-neutral-700"
              >
                <div className="w-full text-neutral-400">
                  <div className="flex flex-row justify-between !mb-[30px]">
                    <div className="h-fit max-w-[100%] overflow-clip flex flex-col">
                      <span >Account No</span>
                      <span className="text-lg">{element.account_no}</span>
                    </div>
                    <div className="h-fit w-[30px] ">
                      {element.platform === "mt5" ? (
                        <Image
                          src={mt5}
                          alt="Background image"
                          // width={"100"} // Set the appropriate width
                          // fill={true}
                          className="h-[30px] w-[30px] object-cover rounded-4xl" // Set the appropriate height
                        />
                      ) : element.platform == "ctrader" ? (
                        <Image
                          src={ctrader}
                          alt="Background image"
                          // width={"100"} // Set the appropriate width
                          // fill={true}
                          className="h-[30px] w-[30px] object-cover rounded-4xl" // Set the appropriate height
                        />
                      ) : (
                        <></>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-row justify-between">
                    <div className="flex flex-col">
                      <span>Server</span>
                      <span className="text-lg">{element.server_name}</span>
                    </div>{" "}
                    <div className="flex flex-col justify-between">
                      {/* <span>Balance</span>
                    <span> $ 4680.00</span> */}
                    </div>
                  </div>

                  {/* <Link href="" className="h-fit">
                <ChartNoAxesCombined size={20} strokeWidth={1} />
              </Link> */}
                </div>
              </Link>
            ))
          ) : (
            <> No account</>
          )}
        </div>
      ) : (
        // Strategy Page
        <div className="w-[100%] !mt-[50px] flex flex-row justify-between">
          {userStrategy!.length > 0 ? (
            userStrategy!.map((element) => (
              <Link
                href="/dashboard/account/statistics"
                className="h-fit w-[30%] bg-neutral-900 rounded-2xl !mb-[20px] !my-auto flex flex-row justify-between items-center !px-7 !py-7 font-light text-neutral-700"
              >
                <div className="w-full text-neutral-400">
                  <div className="flex flex-row justify-between !mb-[30px]">
                    <div className="h-fit max-w-[100%] overflow-clip flex flex-col">
                      <span>Account No</span>
                      <span>{element.account_no}</span>
                    </div>
                    <div className="h-fit w-[20px] ">
                      {element.platform === "mt5" ? (
                        <Image
                          src={mt5}
                          alt="Background image"
                          // width={"100"} // Set the appropriate width
                          // fill={true}
                          className="h-[20px] w-[20px] object-cover rounded-2xl" // Set the appropriate height
                        />
                      ) : element.platform == "ctrader" ? (
                        <Image
                          src={ctrader}
                          alt="Background image"
                          // width={"100"} // Set the appropriate width
                          // fill={true}
                          className="h-[20px] w-[20px] object-cover rounded-2xl" // Set the appropriate height
                        />
                      ) : (
                        <></>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-row justify-between">
                    <div className="flex flex-col">
                      <span>Server</span>
                      <span>{element.server_name}</span>
                    </div>{" "}
                    <div className="flex flex-col justify-between">
                      {/* <span>Balance</span>
                    <span> $ 4680.00</span> */}
                    </div>
                  </div>

                  {/* <Link href="" className="h-fit">
                <ChartNoAxesCombined size={20} strokeWidth={1} />
              </Link> */}
                </div>
              </Link>
            ))
          ) : (
            <>
              {" "}
              <div className="w-[inherit] text-accent-foreground text-center">
                No strategy added yet
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
