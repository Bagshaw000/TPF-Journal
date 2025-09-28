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
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

export default function Page() {
  const data = [1, 2, 3];

  const [pageState, setPageState] = useState(true);
  const handlePageToggle = (element: boolean) => {
    setPageState(element);
  };

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

          {pageState ? (
            // Account Page button
            <div className="w-fit !ml-[10px] !my-auto text-base flex flex-row justify-between items-center font-light">
              <Dialog>
                <form>
                  <DialogTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      className="!mr-[10px] !py-[16px] !px-[12px] text-neutral-400"
                    >
                      <CirclePlus />{" "}
                      <span className="font-light text-sm">
                        
                        Connect new account
                      </span>
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px] !p-[20px]">
                    <DialogHeader>
                      <DialogTitle>Connect a new trading account</DialogTitle>
                      <DialogDescription></DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4">
                      <div className="grid gap-3">
                        <Label htmlFor="name-1">Account Id</Label>
                        <Input
                          id="accId"
                          name="accId"
                          defaultValue="1234567"
                          className="!p-[10px]"
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
                          defaultValue="@peduarte"
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
                      <Button type="submit" className="!p-5">
                        Connect
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </form>
              </Dialog>
              {/* Platform */}
              <Select>
                <SelectTrigger className="w-fit !px-[10px]">
                  <SelectValue placeholder="Filter by platform" />
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
                <form>
                  <DialogTrigger asChild>
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
                    <div className="grid gap-4">
                      <div className="grid gap-3">
                        <Label htmlFor="name">Name</Label>
                        <Input
                          id="name"
                          name="name"
                          defaultValue="Reverse Trend"
                          className="!p-[10px]"
                        />
                      </div>
                      <div className="grid gap-3">
                        <Label htmlFor="entry">Entry logic</Label>
                        <Textarea
                          id="entry"
                          name="entry"
                          defaultValue="Demo-Example-sc"
                          className="!p-[10px]"
                        />
                      </div>
                      <div className="grid gap-3">
                        <Label htmlFor="exit">Exit Logic</Label>
                        <Textarea
                          id="exit"
                          name="exit"
                          defaultValue="Demo-Example-sc"
                          className="!p-[10px]"
                        />
                      </div>
                      <div className="grid gap-3">
                        <Label htmlFor="tp">Take profit criteria</Label>
                        <Textarea
                          id="tp"
                          name="tp"
                          defaultValue="Demo-Example-sc"
                          className="!p-[10px]"
                        />
                      </div>

                      <div className="grid gap-3">
                        <Label htmlFor="sl">Stop loss criteria</Label>
                        <Textarea
                          id="sl"
                          name="sl"
                          defaultValue="Demo-Example-sc"
                          className="!p-[10px]"
                        />
                      </div>
                      <div className="grid gap-3">
                        <Label htmlFor="tm">Trade Management</Label>
                        <Textarea
                          id="tm"
                          name="tm"
                          defaultValue="Demo-Example-sc"
                          className="!p-[10px]"
                        />
                      </div>

                      <div className="flex flex-row justify-between">
                        <div className="grid gap-3 w-[48%]">
                          <Label htmlFor="username-1">Strategy Session</Label>
                          <Select>
                            <SelectTrigger className="w-[100%] !px-[10px]">
                              <SelectValue placeholder="Select platform" />
                            </SelectTrigger>
                            <SelectContent className="w-fit h-fit gap-1 ">
                              <SelectGroup>
                                <SelectLabel>Session</SelectLabel>
                                <SelectItem value="Asian">Asian</SelectItem>
                                <SelectItem value="London">London</SelectItem>
                                <SelectItem value="New York">
                                  New York
                                </SelectItem>
                                <SelectItem value="Sydney">Sydney</SelectItem>
                                <SelectItem value="None">None</SelectItem>
                              </SelectGroup>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="grid gap-3 w-[48%]">
                          <Label htmlFor="username-1">Risk Profile</Label>
                          <Select>
                            <SelectTrigger className="!px-[10px] w-[100%]">
                              <SelectValue placeholder="Select platform" />
                            </SelectTrigger>
                            <SelectContent className="w-fit h-fit gap-1 ">
                              <SelectGroup>
                                <SelectLabel>Risk Profile</SelectLabel>
                                <SelectItem value="None">high</SelectItem>
                                <SelectItem value="medium">medium</SelectItem>
                                <SelectItem value="low">low</SelectItem>
                              </SelectGroup>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div className="grid gap-3 w-[48%]">
                        <Label htmlFor="username-1">Strategy Status</Label>
                        <Select>
                          <SelectTrigger className="w-full !px-[10px]">
                            <SelectValue placeholder="Select status" />
                          </SelectTrigger>
                          <SelectContent className="w-fit h-fit gap-1 ">
                            <SelectGroup>
                              <SelectLabel>Status</SelectLabel>
                              <SelectItem value="Active">Active</SelectItem>
                              <SelectItem value="Testing">Testing</SelectItem>
                              <SelectItem value="Retired">Retired</SelectItem>
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
                      <Button type="submit" className="!p-5">
                        Add Strategy
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </form>
              </Dialog>
            </>
          )}
        </div>
      </div>

      {/* List all user trading account linked */}
      {pageState ? (
        // Account page
        <div className="w-[100%] !mt-[50px] flex flex-row justify-between">
          {data.map((element) => (
            <Link
              href="/dashboard/account/statistics"
              className="h-fit w-[30%] bg-neutral-900 rounded-2xl !mb-[20px] !my-auto flex flex-row justify-between items-center !px-7 !py-7 font-light text-neutral-700"
            >
              <div className="w-full text-neutral-400">
                <div className="flex flex-row justify-between !mb-[30px]">
                  <div className="h-fit max-w-[100%] overflow-clip flex flex-col">
                    <span>Account Name</span>
                    <span>Omieibi Bagshaw</span>
                  </div>
                  <div className="h-fit w-[20px] ">
                    <Image
                      src={mount}
                      alt="Background image"
                      // width={"100"} // Set the appropriate width
                      // fill={true}
                      className="h-[20px] w-[20px] object-cover rounded-2xl" // Set the appropriate height
                    />
                  </div>
                </div>

                <div className="flex flex-row justify-between">
                  <div className="flex flex-col">
                    <span>Account No</span>
                    <span>Omieibi Bagshaw</span>
                  </div>{" "}
                  <div className="flex flex-col justify-between">
                    <span>Balance</span>
                    <span> $ 4680.00</span>
                  </div>
                </div>

                {/* <Link href="" className="h-fit">
                <ChartNoAxesCombined size={20} strokeWidth={1} />
              </Link> */}
              </div>
            </Link>
          ))}
        </div>
      ) : (
        // Strategy Page
        <div className="w-[100%] !mt-[50px] flex flex-row justify-between">
          {data.map((element) => (
            <Link
              href="#"
              className="h-fit w-[30%] bg-neutral-900 rounded-2xl !mb-[20px] !my-auto flex flex-row justify-between items-center !px-7 !py-7 font-light text-neutral-700"
            >
              <div className="w-full text-neutral-400">
                <div className="flex flex-row justify-between !mb-[30px]">
                  <div className="h-fit max-w-[100%] overflow-clip flex flex-col">
                    <span>Strategy Name</span>
                    <span>Omieibi Bagshaw</span>
                  </div>
                  <div className="h-fit flex flex-col">
                    <span>Category</span>
                    <span>Omieibi </span>
                  </div>
                </div>

                <div className="flex flex-row justify-between">
                  <div className="flex flex-col">
                    <span>Performance</span>
                    <span>Omieibi Bagshaw</span>
                  </div>
                  <div className="flex flex-col justify-between">
                    <span>Balance</span>
                    <span> $ 4680.00</span>
                  </div>
                </div>

                {/* <Link href="" className="h-fit">
                <ChartNoAxesCombined size={20} strokeWidth={1} />
              </Link> */}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
