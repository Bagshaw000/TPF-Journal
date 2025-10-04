// app/dashboard/page.tsx
"use client";
import { useForm } from "react-hook-form";
import {
  useMemo,
  Fragment,
  useState,
  useEffect,
  JSXElementConstructor,
  ReactElement,
  ReactNode,
  ReactPortal,
} from "react";

// import {  AreaChart, BarChart, PieChart, TrendingUp } from "lucide-react";
import Link from "next/link";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  ChartConfig,
} from "@/components/ui/chart";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  Pie,
  PieChart,
  Rectangle,
  Tooltip,
  XAxis,
} from "recharts";

import { Calendar, Views, dateFnsLocalizer } from "react-big-calendar";
import { format, parse, startOfWeek, getDay } from "date-fns";
import { TrendingUp } from "lucide-react";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
  Form,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
// import { Form } from "react-hook-form";
import { symbol, z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import EmojiRating from "@/components/emoji-rating";
import Calendar21 from "@/components/calendar-21";
import { useSearchParams } from "next/navigation";
import client from "@/api/client";
type PerformanceEntry = {
  total: string | number;
  long: string | number;
  short: string | number;
};

type Trade = {
  account_id: number;
  commission: number;
  created_at: string; // ISO timestamp
  emotion_tag: string | null;
  entry_price: number;
  entry_time: string; // ISO timestamp
  exit_price: number;
  exit_time: string; // ISO timestamp
  fee: number;
  id: number;
  pos_trade_note: string | null;
  position_id: number;
  pre_trade_note: string | null;
  profit_loss: number;
  current_price: number | null;
  sl_price: number;
  strategy_tag: string | null;
  swap: number;
  symbol: string;
  tp_price: number;
  trade_images: {
    pre_trade: string | null;
    post_trade: string | null;
  };
  trade_type: "buy" | "sell";
  volume: number;
};

export default function Page() {
  const [pageState, setPageState] = useState(true);
  const handlePageToggle = (element: boolean) => {
    setPageState(element);
  };

  const [subPageState, setSubPageState] = useState(true);
  const handleSubPageToggle = (element: boolean) => {
    setSubPageState(element);
  };

  const [tradePageState, setTradePageState] = useState(true);
  const handleTradePageToggle = (element: boolean) => {
    setTradePageState(element);
  };

  const [tradeDetailState, setTradeDetailState] = useState(false);
  const handleTradeDetailState = (element: boolean, data: Trade | null) => {
    console.log(data);
    setTradeDetailState(element);
    setTradeDetails(data);
  };

  const formSchema = z.object({
    strategy: z.string(),

    preTradeLink: z.string(),
    postTradeLink: z.string(),
    preTradeNote: z.string(),
    postTradeNote: z.string(),
  });

  const options: Intl.DateTimeFormatOptions = {
    day: "2-digit",
    month: "short",
    year: "numeric",
  };

  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      strategy: "",
      preTradeLink: "",
      postTradeLink: "",
      preTradeNote: "",
      postTradeNote: "",
    },
  });

  // 2. Define a submit handler.
  async function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values.
    // ✅ This will be type-safe and validated.

    let strategyStatus: string | null = values.strategy;

    if (values.strategy === "") {
      strategyStatus = null;
    }

    const openTradeJournal = {
      strategy_tag: parseInt(strategyStatus!) || null,
      pre_trade_note: values.preTradeNote,
      pos_trade_note: values.postTradeNote,
      trade_images: {
        pre_trade: values.preTradeLink,
        post_trade: values.postTradeLink,
      },
      emotion_tag: {
        pre_trade: beforeRating,
        post_trade: afterRating,
      },
    };

    // For completed trade
    if (
      tradeDetail?.current_price !== null ||
      tradeDetail.current_price !== undefined
    ) {
      const acc = await supabase
        .from("trade_history")
        .update(openTradeJournal)
        .eq("id", tradeDetail?.id!);

      if (acc.data) {
        // Show a toast of succes
      } else {
        // Show a toast
      }
    } else {
      // Else update close position based on id
      const acc = await supabase
        .from("open_trade")
        .update(openTradeJournal)
        .eq("id", tradeDetail?.id!);
      if (!acc.data) {
        const updateHist = await supabase
          .from("trade_history")
          .update(openTradeJournal)
          .eq("id", tradeDetail?.id!);

        if (updateHist.data) {
          // Toast issue
        }
      } else {
        // Show toast of the succes
      }
    }
    setAfterRating(0);
    setBeforeRating(0);
  }

  function averageDateFormat(dateStr: string) {
    
    if (dateStr && typeof dateStr === "string" && dateStr !== "0" ) {
      // Split into days and time
      const [daysPart, timePart] = dateStr.split(", ");
      

      const days = parseInt(daysPart, 10) || 0;

      // Extract time (HH:MM:SS.mmm)
      const [hours, minutes, secondsPart] = timePart.split(":");
      const hoursNum = parseInt(hours) || 0;
      const minutesNum = parseInt(minutes) || 0;
      const secondsNum = Math.floor(parseFloat(secondsPart)) || 0;

      // Pick a base date (example: now)
      const seconds = Math.floor(parseFloat(secondsPart)); // remove milliseconds

// Build formatted string
let result = "";
if (days) result += `${days} days `;
if (hours) result += `${parseInt(hours)} hours `;
if (minutes) result += `${parseInt(minutes)} min `;
if (seconds) result += `${seconds} sec`;
      return result;
    } else {
      return dateStr;
    }
  }

  const [beforeRating, setBeforeRating] = useState(0);
  const [afterRating, setAfterRating] = useState(0);

  const urlParams = useSearchParams();
  const account_id = urlParams.get("id");

  const [accPerf, setAccPerf] = useState<null | Array<any>>([]);
  const [perPeriod, setPerPeriod] = useState<any>({});
  const [togglePeriod, setTogglePeriod] = useState<string>("*");
  const [pastTrade, setPastTrade] = useState<null | Array<any>>([]);
  const [tradeDetail, setTradeDetails] = useState<Trade | null>();
  const [liveTrade, setLiveTrade] = useState<null | Array<any>>([]);
  const [userStrategy, setUserStrategy] = useState<null | Array<any>>([]);
  const supabase = client;

  // console.log(data)
  useEffect(() => {
    const fetchUserAccount = async () => {
      const acc = await supabase
        .from("performance")
        .select("*")
        .eq("account_id", parseInt(account_id!));

      const pastTrade = await supabase
        .from("trade_history")
        .select("*")
        .eq("account_id", parseInt(account_id!))
        .order("entry_time", { ascending: false })
        .or("trade_type.eq.sell, trade_type.eq.buy");

      setPastTrade(pastTrade.data);

      if (acc.data) {
        const newArray = acc.data.reduce((accObj: any, currentVal: any) => {
          const performance = JSON.parse(currentVal.performance);
          currentVal.performance = performance;
          accObj[currentVal.period] = currentVal; // key by period
          return accObj;
        }, {});

        setPerPeriod(newArray);
      }

      setAccPerf(acc.data);
      // setUserStrategy(strategy.data);
    };

    const fetchLiveTrade = async () => {
      const liveTrade = await supabase
        .from("open_trade")
        .select("*")
        .eq("account_id", parseInt(account_id!))
        .order("entry_time", { ascending: false })
        .or("trade_type.eq.sell, trade_type.eq.buy");

      // console.log(liveTrade.data);
      setLiveTrade(liveTrade.data);
    };

    const getUserStrategy = async () => {
      const userId = (await client.auth.getUser()).data.user?.id;
      const allUserStrategy = await supabase
        .from("strategy")
        .select("*")
        .eq("user_id", userId);

      setUserStrategy(allUserStrategy.data);
    };
    getUserStrategy();
    fetchUserAccount();

    const interval = setInterval(() => {
      fetchLiveTrade();
    }, 15000); // every 5 seconds

    // Cleanup on unmount
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="!px-[5%]">
      {/* Navigation Toggle*/}
      <div className="w-[100%]  !mx-auto  border-b-2 !my-[50px]">
        <div className="!mb-[10px] flex flex-row">
          <button
            className="!mr-[20px] "
            onClick={() => handlePageToggle(true)}
          >
            Performance
            {pageState ? (
              <hr className="border-spacing-1.5 bg-blue-500" />
            ) : (
              <hr className="hidden" />
            )}
          </button>
          <button onClick={() => handlePageToggle(false)}>
            Trades
            {!pageState ? (
              <hr className="border-1.5 bg-blue-500" />
            ) : (
              <hr className="hidden" />
            )}
          </button>
        </div>
      </div>

      {/* Performance Dashboard */}
      {pageState ? (
        <div className="w-[100%]">
          <h1 className="text-3xl ">Performance</h1>
          <p className="!mt-2 text-muted-foreground">
            This dashboard shows  performance metrics of this account
          </p>

          <div className="!mt-[50px]">
            <div className="">
              {/* Return Metrics */}
              <div className="!mb-[100px]">
                <h1 className="text-3xl !mb-[20px]">Return Metrics</h1>

                {/* First line of Metrics */}
                <div className="flex flex-row justify-between w-[100%] !mb-[40px]">
                  <Card className="md:w-[23%] md:h-[200px] rounded-2xl  !p-[20px] ">
                    <CardHeader>
                      <CardTitle>Net Profit {}</CardTitle>
                      <CardDescription>
                        Showing total visitors for the last 6 months
                      </CardDescription>
                    </CardHeader>

                    <h3 className="text-2xl !mt-[20px]">
                      {perPeriod["*"]?.performance?.[
                        "Net profit"
                      ].total.toFixed(2)}
                    </h3>
                  </Card>

                  <Card className="md:w-[23%] md:h-[200px] rounded-2xl  flex flex-col !p-[20px] ">
                    <CardHeader>
                      <CardTitle>Profit Percentage</CardTitle>
                      <CardDescription>
                        Showing total visitors for the last 6 months
                      </CardDescription>
                    </CardHeader>
                    <h3 className="text-2xl !mt-[20px]">
                      {perPeriod["*"]?.performance?.[
                        "Percentage return"
                      ].total.toFixed(2)}
                    </h3>
                  </Card>

                  <Card className="md:w-[23%] md:h-[200px] rounded-2xl  flex flex-col !p-[20px] ">
                    <CardHeader>
                      <CardTitle>Total Trades</CardTitle>
                      <CardDescription>
                        Showing total visitors for the last 6 months
                      </CardDescription>
                    </CardHeader>
                    <h3 className="text-2xl !mt-[20px]">
                      {perPeriod["*"]?.performance?.[
                        "Total trades"
                      ].total.toFixed(2)}
                    </h3>
                  </Card>

                  <Card className="md:w-[23%] md:h-[200px] rounded-2xl  flex flex-col !p-[20px] ">
                    <CardHeader>
                      <CardTitle>Average Return per trade</CardTitle>
                      <CardDescription>
                        Showing total visitors for the last 6 months
                      </CardDescription>
                    </CardHeader>
                    <h3 className="text-2xl !mt-[20px]">
                      {perPeriod["*"]?.performance?.[
                        "Average trade"
                      ].total.toFixed(2)}
                    </h3>
                  </Card>
                </div>

                <div className="!mb-[50px] hidden">
                  {/* Second line of Metrics */}
                  <div className="flex flex-row justify-between">
                    <Card className="md:w-[32%] md:h-[200px] rounded-2xl !p-[20px] ">
                      <CardHeader>
                        <CardTitle>Average risk per trade</CardTitle>
                        <CardDescription>
                          Showing total visitors for the last 6 months
                        </CardDescription>
                      </CardHeader>

                      <h3>2000</h3>
                    </Card>

                    <Card className="md:w-[32%] md:h-[200px] rounded-2xl !p-[20px] ">
                      <CardHeader>
                        <CardTitle>Exposure</CardTitle>
                        <CardDescription>
                          Showing total visitors for the last 6 months
                        </CardDescription>
                      </CardHeader>

                      <h3>2000</h3>
                    </Card>

                    <Card className="md:w-[32%] md:h-[200px] rounded-2xl !p-[20px]">
                      <CardHeader>
                        <CardTitle>Percentage Max Drawdown</CardTitle>
                        <CardDescription>
                          Showing total visitors for the last 6 months
                        </CardDescription>
                      </CardHeader>

                      <h3>2000</h3>
                    </Card>
                  </div>
                </div>

                {/* Third line of Return Metrics*/}
              </div>

              {/* Trade Statisitics*/}
              <div className="!mb-[100px]">
                <h1 className="text-3xl !mb-[20px]">Trade Statistics</h1>

                <div className="!mb-[10px]  w-[350px] justify-between flex flex-row">
                  <button
                    className=""
                    onClick={() => handleSubPageToggle(true)}
                  >
                    General
                    {subPageState ? (
                      <hr className="border-spacing-1.5 bg-blue-500" />
                    ) : (
                      <hr className="hidden" />
                    )}
                  </button>
                  <button onClick={() => handleSubPageToggle(false)}>
                    Symbols
                    {!subPageState ? (
                      <hr className="border-spacing-1.5 bg-blue-500" />
                    ) : (
                      <hr className="hidden" />
                    )}
                  </button>

                  {/* Select button */}
                  <Select>
                    <SelectTrigger className="w-[180px] !px-[0.5%]">
                      <SelectValue placeholder="Period" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup className="!px-[5%]">
                        <SelectLabel>Period</SelectLabel>
                        <SelectItem value="*">All history</SelectItem>
                        <SelectItem
                          value="t-w"
                          onClick={() => setTogglePeriod("t-w")}
                        >
                          This week
                        </SelectItem>
                        <SelectItem
                          value="t-m"
                          onClick={() => setTogglePeriod("t-m")}
                        >
                          Current Month
                        </SelectItem>
                        <SelectItem
                          value="l-m"
                          onClick={() => setTogglePeriod("l-m")}
                        >
                          Previous Month
                        </SelectItem>
                        <SelectItem
                          value="3-m"
                          onClick={() => setTogglePeriod("3-m")}
                        >
                          Last 3 months{" "}
                        </SelectItem>
                        <SelectItem
                          value="6-m"
                          onClick={() => setTogglePeriod("6-m")}
                        >
                          Last 6 months
                        </SelectItem>
                        <SelectItem
                          value="12-m"
                          onClick={() => setTogglePeriod("12-m")}
                        >
                          Last year
                        </SelectItem>
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                </div>

                {subPageState ? (
                  // General Statisitics
                  <div>
                    <Table>
                      <TableHeader>
                        <TableRow className="text-zinc-800 text-base">
                          <TableHead className="w-[40%]">Summary</TableHead>
                          <TableHead className="text-right">
                            All trades
                          </TableHead>
                          <TableHead className="text-right">
                            Long Trades
                          </TableHead>
                          <TableHead className="text-right">
                            {" "}
                            Short Trades
                          </TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {/* For loop */}

                        {Object.entries(
                          perPeriod[togglePeriod]?.performance || {}
                        ).map(([key, value]) =>
                          key === "period" ? (
                            <div key={key}></div>
                          ) : [
                              "Average trade duration",
                              "Average win trade duration",
                              "Average loss trades duration",
                            ].includes(key) ? (
                            <TableRow key={key}>
                              <TableCell className="font-normal text-lg">
                                {key}
                              </TableCell>
                              {(() => {
                                const perf = value as {
                                  total: string;
                                  long: string;
                                  short: string;
                                };
                                return (
                                  <>
                                    <TableCell className="text-right text-lg">
                                      {
                                        averageDateFormat(
                                          perf.total! as string
                                        ) as string
                                      }
                                    </TableCell>
                                    <TableCell className="text-right text-lg">
                                      {
                                        averageDateFormat(
                                          perf.long! as string
                                        ) as string
                                      }
                                    </TableCell>
                                    <TableCell className="text-right text-lg">
                                      {
                                        averageDateFormat(
                                          perf.short! as string
                                        ) as string
                                      }
                                    </TableCell>
                                  </>
                                );
                              })()}
                            </TableRow>
                          ) : (
                            <TableRow key={key}>
                              <TableCell className="font-normal text-lg">
                                {key}
                              </TableCell>
                              {(() => {
                                const perf = value as {
                                  total: string | number;
                                  long: string | number;
                                  short: string | number;
                                };
                                return (
                                  <>
                                    <TableCell className="text-right text-lg">
                                      {typeof perf.total === "number"
                                        ? perf.total.toFixed(2)
                                        : String(perf.total)}
                                    </TableCell>
                                    <TableCell className="text-right text-lg">
                                      {typeof perf.long === "number"
                                        ? perf.long.toFixed(2)
                                        : String(perf.long)}
                                    </TableCell>
                                    <TableCell className="text-right text-lg">
                                      {typeof perf.short === "number"
                                        ? perf.short.toFixed(2)
                                        : String(perf.short)}
                                    </TableCell>
                                  </>
                                );
                              })()}
                            </TableRow>
                          )
                        )}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  // Symbol statisitic
                  <div>
                    <Table>
                      <TableHeader>
                        <TableRow className="text-zinc-800">
                          <TableHead className="w-[10%]"></TableHead>
                          <TableHead className="w-[20%] text-center bg-accent">
                            Long Trades
                          </TableHead>
                          <TableHead className="w-[20%] text-center">
                            Short Trades
                          </TableHead>
                          <TableHead className="w-[30%] text-center bg-accent">
                            Total
                          </TableHead>
                        </TableRow>

                        <TableRow className="text-zinc-800  ">
                          <TableHead className="w-[10%]">Symbol</TableHead>

                          <TableHead className="w-[20%] bg-accent">
                            <div className="flex flex-row justify-between w-[80%] items-center  !mx-auto">
                              <span>Trades</span>
                              <span>Pips</span>
                              <span>Net profit</span>
                            </div>
                          </TableHead>

                          <TableHead className="w-[20%]">
                            <div className="flex flex-row justify-between w-[80%] items-center  !mx-auto">
                              <span>Trades</span>
                              <span>Pips</span>
                              <span>Net profit</span>
                            </div>
                          </TableHead>

                          <TableHead className="w-[20%] bg-accent">
                            <div className="flex flex-row justify-between w-[80%] items-center !mx-auto">
                              <span>Trades</span>
                              <span>Pips</span>
                              <span>Net profit</span>
                              <span> Won (%)</span>
                              <span>Lost (%)</span>
                            </div>
                          </TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow>
                          <TableCell className="font-medium">INV001</TableCell>
                          <TableCell className="text-right">Paid</TableCell>
                          <TableCell className="text-right">
                            Credit Card
                          </TableCell>
                          <TableCell className="text-right">$250.00</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* Trades Page */}
          <div className="!mb-[50px]">
            {" "}
            <h1 className="font-medium text-3xl">Trades</h1>
            <div className="!mt-2 text-muted-foreground">
              View live and past profitable trades, and journal your strategies
              for improvement.
            </div>
          </div>
          <div className="!mb-[10px]  w-full justify-between flex flex-row">
            <div className="w-[100px] flex flex-row justify-between">
              <button className="" onClick={() => handleTradePageToggle(true)}>
                Live
                {tradePageState ? (
                  <hr className="border-spacing-1.5 bg-blue-500" />
                ) : (
                  <hr className="hidden" />
                )}
              </button>
              <button onClick={() => handleTradePageToggle(false)}>
                History
                {!tradePageState ? (
                  <hr className="border-spacing-1.5 bg-blue-500" />
                ) : (
                  <hr className="hidden" />
                )}
              </button>
            </div>

            {/* Select button (History) */}
            {!tradePageState ? (
              <div className="">
                <Select>
                  <SelectTrigger className="w-[180px] !px-[2%]">
                    <SelectValue placeholder="Period" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup className="!px-[5%]">
                      <SelectLabel>Period</SelectLabel>
                      <SelectItem value="all">All history</SelectItem>
                      <SelectItem value="week">This week</SelectItem>
                      <SelectItem value="month">Current Month</SelectItem>
                      <SelectItem value="last-month">Previous Month</SelectItem>
                      <SelectItem value="3-month">Last 3 months </SelectItem>
                      <SelectItem value="6-month">Last 6 months</SelectItem>
                      <SelectItem value="year">Last year</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
            ) : (
              <></>
            )}
          </div>
          {/* Trade Statitistics */}
          <div className="flex flex-row ">
            {/* // loop through live trades */}
            <div className="w-full">
              <Table>
                <TableCaption> All current trades on this account</TableCaption>
                <TableHeader>
                  <TableRow className="text-base">
                    {/* <TableHead colSpan={1}></TableHead> */}
                    <TableHead className="">Symbol</TableHead>
                    <TableHead className="">Trade ID</TableHead>
                    <TableHead className="">Trade Type</TableHead>
                    {/* <TableHead className="w-[100px]">Take Profit</TableHead>
                    <TableHead className="w-[100px]">Stop Loss</TableHead> */}
                    {/* <TableHead className="">Current Price</TableHead> */}
                    <TableHead className="">Date</TableHead>
                    {/* <TableHead> Action</TableHead> */}
                    {/* <TableHead>Method</TableHead> */}
                    <TableHead className="">Amount</TableHead>
                  </TableRow>
                </TableHeader>
                {tradePageState ? (
                  // Live trades
                  <TableBody
                    className={`transition-all duration-300 ${
                      tradeDetailState ? "w-1/3" : "w-full"
                    }`}
                  >
                    {/* <button> */}
                    {liveTrade !== null ? (
                      <>
                        {liveTrade!.map((element) => (
                          <TableRow
                            onClick={() =>
                              handleTradeDetailState(true, element)
                            }
                            className="h-[60px] !my-auto text-lg"
                          >
                            {/* <Checkbox className="!my-auto"></Checkbox> */}

                            <TableCell className=" !my-auto">
                              {element.symbol}
                            </TableCell>
                            <TableCell>{element.position_id}</TableCell>
                            <TableCell>
                              {element.trade_type == "buy" ? (
                                <div className="w-fit !px-6 rounded-2xl font-medium  bg-emerald-200 text-emerald-800">
                                  Buy
                                </div>
                              ) : (
                                <div className="w-fit !px-6 rounded-2xl font-medium  bg-red-300 text-red-500">
                                  Sell
                                </div>
                              )}
                            </TableCell>
                            {/* <TableCell className="">$250.00</TableCell> */}
                            <TableCell className="">
                              {new Date(
                                element?.entry_time as string
                              ).toLocaleDateString("en-GB", options)}
                            </TableCell>
                            <TableCell className="">
                              {element.profit_loss}
                            </TableCell>
                          </TableRow>
                        ))}
                      </>
                    ) : (
                      <>
                        {" "}
                        <h1 className="text-center"> No Open Trades</h1>
                      </>
                    )}

                    {/* </button> */}
                  </TableBody>
                ) : (
                  // History
                  <TableBody
                    className={`transition-all duration-300 ${
                      tradeDetailState ? "w-1/3" : "w-full"
                    }`}
                  >
                    {}

                    {pastTrade!.map((element) => (
                      <TableRow
                        onClick={() => handleTradeDetailState(true, element)}
                        className="h-[60px] !my-auto text-lg"
                      >
                        {/* <Checkbox className="!my-auto"></Checkbox> */}

                        <TableCell className=" !my-auto">
                          {element.symbol}
                        </TableCell>
                        <TableCell>{element.position_id}</TableCell>
                        <TableCell>
                          {element.trade_type =="buy" ? (
                            <div className="w-fit !px-6 rounded-2xl font-medium  bg-emerald-200 text-emerald-800">
                              Buy
                            </div>
                          ) : (
                            <div className="w-fit !px-6 rounded-2xl font-medium  bg-red-300 text-red-500">
                              Sell
                            </div>
                          )}
                        </TableCell>
                        {/* <TableCell className="">$250.00</TableCell> */}
                        <TableCell className="">
                          {new Date(
                            element?.entry_time as string
                          ).toLocaleDateString("en-GB", options)}
                        </TableCell>
                        <TableCell className="">
                          {element.profit_loss}
                        </TableCell>
                      </TableRow>
                    ))}

                    {/* </button> */}
                  </TableBody>
                )}
              </Table>
            </div>

            <div
              className={`  transition-all duration-300  min-h-fit !p-[1%]  rounded-3xl border-2 border-accent ${
                tradeDetailState ? "w-2/3" : "hidden"
              }`}
            >
              {/* Close button */}
              <div className="flex flex-row w-full justify-between">
                <div>
                  <h2 className=" text-2xl mb-2">Journal</h2>
                  <p>Journal your trade</p>
                </div>
                <button
                  onClick={() => handleTradeDetailState(false, null)}
                  className="!mt-4 !px-3 !py-1 rounded bg-red-500 text-white"
                >
                  Close
                </button>
              </div>

              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="space-y-8"
                >
                  <FormField
                    control={form.control}
                    name="strategy"
                    render={({ field }) => (
                      <FormItem>
                        <div className="text-neutral-500">
                          <div className="flex flex-row justify-between items-center">
                            <div className="text-neutral-500">
                              <h1 className="text-lg !my-5">
                                {" Symbol: "}
                                {tradeDetail?.symbol}
                              </h1>
                            </div>
                            <span className="text-lg">
                              Date:{" "}
                              {new Date(
                                tradeDetail?.entry_time as string
                              ).toLocaleDateString("en-GB", options)}
                            </span>
                            <Select
                              onValueChange={field.onChange}
                              defaultValue={field.value}
                            >
                              <FormControl>
                                <SelectTrigger className="!px-[10px]">
                                  <SelectValue placeholder="Select a strategy" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent className="!px-[5px]">
                                {/* For loop through the item */}

                                <SelectGroup className="!px-[5%]">
                                  <SelectLabel>Period</SelectLabel>
                                  {userStrategy ? (
                                    userStrategy?.map((element) => (
                                      <SelectItem
                                        value={element.id.toString()}
                                        className="!px-[10px]"
                                      >
                                        {element.name}
                                      </SelectItem>
                                    ))
                                  ) : (
                                    <SelectItem value="">
                                      No strategy
                                    </SelectItem>
                                  )}
                                </SelectGroup>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div>
                    <span> Details </span>
                  </div>
                  <div className=" w-[100%] flex flex-col justify-between text-neutral-500 !mb-[20px]">
                    <Table className="">
                      <TableHeader className="border-0">
                        <TableRow className="border-0">
                          {/* <TableHead colSpan={1}></TableHead> */}

                          <TableHead
                            className="border-0 hidden"
                            colSpan={4}
                          ></TableHead>
                        </TableRow>
                      </TableHeader>

                      <TableBody
                        className={`transition-all duration-300 w-full border-0`}
                      >
                        {/* <button> */}

                        <TableRow className="h-[60px] !my-auto border-0">
                          {/* <Checkbox className="!my-auto"></Checkbox> */}
                          <TableCell className="font-medium !my-auto">
                            Trade ID : {tradeDetail?.position_id}
                          </TableCell>
                          <TableCell>Swap : {tradeDetail?.swap || 0}</TableCell>
                          <TableCell>
                            Commission : {tradeDetail?.commission || 0}
                          </TableCell>
                          <TableCell>Fee : {tradeDetail?.fee || 0}</TableCell>
                        </TableRow>
                        <TableRow className="h-[60px] !my-auto border-0">
                          {/* <Checkbox className="!my-auto"></Checkbox> */}
                          <TableCell className="font-medium !my-auto">
                            Entry Price : {tradeDetail?.entry_price}
                          </TableCell>
                          <TableCell>
                            Profit : {tradeDetail?.profit_loss}
                          </TableCell>
                          <TableCell>
                            Target : {tradeDetail?.tp_price}
                          </TableCell>
                          <TableCell>
                            Stoploss : {tradeDetail?.sl_price}
                          </TableCell>
                        </TableRow>
                        <TableRow className="h-[60px] !my-auto border-0">
                          {/* <Checkbox className="!my-auto"></Checkbox> */}
                          <TableCell className="font-medium !my-auto">
                            Volume : {tradeDetail?.volume}
                          </TableCell>
                          <TableCell>
                            Trade type : {tradeDetail?.trade_type}
                          </TableCell>
                          {/* <TableCell>Credit Card</TableCell> */}
                        </TableRow>

                        {/* </button> */}
                      </TableBody>
                    </Table>
                  </div>
                  <FormField
                    control={form.control}
                    name="preTradeLink"
                    render={({ field }) => (
                      <FormItem>
                        {/* For the embeded link if nothing is returned then display the input field  else display the embededd link */}
                        <div className="!mb-[10px]">
                          <FormLabel className="!mb-[10px]">
                            Pre Trade link
                          </FormLabel>
                          <FormControl>
                            {/* <Textarea placeholder="Type your message here." {...field} className="h-[300px] !p-1"/> */}
                            <Input
                              {...field}
                              placeholder={
                                tradeDetail?.trade_images?.pre_trade! ||
                                "Enter your pre trade link"
                              }
                              className="!p-2"
                            />
                          </FormControl>
                        </div>
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="postTradeLink"
                    render={({ field }) => (
                      <FormItem className="!mb-[20px]">
                        {/* For the embeded link if nothing is returned then display the input field  else display the embededd link */}
                        <div className="!mb-[10px]">
                          <FormLabel className="!mb-[10px]">
                            Post Trade link
                          </FormLabel>
                          <FormControl>
                            {/* <Textarea placeholder="Type your message here." {...field} className="h-[300px] !p-1"/> */}
                            <Input
                              {...field}
                              placeholder={
                                tradeDetail?.trade_images?.post_trade! ||
                                "Enter your post trade link"
                              }
                              className="!p-2"
                            />
                          </FormControl>
                        </div>
                      </FormItem>
                    )}
                  />

                  <div className="flex flex-row w-full justify-between">
                    <FormField
                      control={form.control}
                      name="preTradeNote"
                      render={({ field }) => (
                        <FormItem className=" w-[48%]">
                          {/* For the embeded link if nothing is returned then display the input field  else display the embededd link */}

                          <div className=" w-[100%]">
                            <FormLabel className="!mb-[10px]">
                              Pre Trade
                            </FormLabel>
                            <FormControl>
                              <Textarea
                                placeholder={
                                  tradeDetail?.pre_trade_note! ||
                                  "Enter your pre trade notes"
                                }
                                {...field}
                                className="h-[300px] !p-1"
                              />
                            </FormControl>
                          </div>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="postTradeNote"
                      render={({ field }) => (
                        <FormItem className=" w-[48%]">
                          <div className=" w-[100%]">
                            <FormLabel className="!mb-[10px]">
                              Post Trade
                            </FormLabel>
                            <FormControl>
                              <Textarea
                                placeholder={
                                  tradeDetail?.pos_trade_note! ||
                                  "Enter your post trade notes"
                                }
                                {...field}
                                className="h-[300px] !p-1"
                              />
                            </FormControl>
                          </div>
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="flex flex-row w-full justify-between !mb-[50px]">
                    <div className="w-[47%] !mt-[30px]">
                      <h5 className="!my-[10px] w-[100%]">
                        Rate your Pre trade emotion
                      </h5>

                      <EmojiRating
                        value={beforeRating}
                        onChange={setBeforeRating}
                      />
                    </div>

                    <div className="w-[47%] !mt-[30px]">
                      <h5 className="!my-[10px] w-[100%]">
                        Rate your Post trade emotion
                      </h5>
                      <EmojiRating
                        value={afterRating}
                        onChange={setAfterRating}
                      />
                    </div>
                  </div>

                  <Button type="submit" className="!px-[20px]">
                    Submit
                  </Button>
                </form>
              </Form>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
