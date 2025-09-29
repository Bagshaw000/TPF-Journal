"use client";
import useSWR, { SWRConfig } from 'swr'
import Image from "next/image";
import styles from "./page.module.css";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardAction,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import home1 from "../../videos/home.mp4";
import Video from "next-video";
import mount from "../../public/mount.svg";
import Link from "next/link";
import { Fullscreen } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";
// import { createClient } from "../utils/supabase/server";
import {} from "@supabase/supabase-js"
import useAuth from '@/hooks/useAuth';
import client from '@/api/client';

import { AuthContextType } from '@/components/context/AuthProvider';

export default function Home() {
  const {user, loading} = useAuth() as AuthContextType
  const [signup, setSignup] = useState(false);
  const router = useRouter();
  // const supabase = createClient();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  if(!loading && user){
    // router.push("/dashboard/account");
  }
  async function logIn() {
    const { data,error } = await client.auth.signInWithPassword({
      email,
      password,
    });
    console.log(data)
    if(data){
      router.push("/dashboard/account");
    }
    if (error) {
      console.error(error);
    }
    
  }

  async function signUp() {
    const { data,error } = await client.auth.signUp({ email, password });
    console.log(data)
    if (error) {
      console.error(error);
    }
    router.push("/");
  }

  // const {data: accounts} = useSWR()
  // handleClick() {

  // }
  return (
    <div className="flex  flex-col md:flex-row w-[100vw] h-[100vh] bg-gray-950">
      <div className="w-[100%] h-[65%] md:w-[65%]">
        <Image
          src={mount}
          alt="Background image"
          // width={"100"} // Set the appropriate width
          // fill={true}
          className="h-[100%] md:h-[100vh] object-cover" // Set the appropriate height
        />
      </div>
      <div className="flex flex-col justify-center  items-center w-[100%] mx-auto text-amber-50 h-[50%]  md:w-[45%] md:my-auto md:h-[100%] ">
        <div className="w-[80%] max-w-[500px] h-[300px]  my-auto flex flex-col justify-between md:w-[80%]">
          {signup ? (
            // Login Page
            <Card className="w-[100%]  bg-transparent !p-5">
              <CardHeader>
                <CardTitle className="text-amber-50">
                  Login to your account
                </CardTitle>

                <CardDescription>
                  Enter your email below to login to your account
                </CardDescription>
                <CardAction>
                  <Button
                    variant="link"
                    className="text-amber-50"
                    onClick={() => setSignup(!signup)}
                  >
                    Signup
                    {/* <Link href="/signup" >Signup</Link> */}
                  </Button>
                </CardAction>
              </CardHeader>

              <CardContent className="w-[100%]">
                <form>
                  <div className="flex flex-col gap-6 w-[100%]">
                    <div className="grid gap-2 w-[100%]  text-amber-50">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="m@example.com"
                        required
                        className="px-4 text-amber-50"

                        onChange={(e) => setEmail(e.target.value)}
                      />
                    </div>
                    <div className="grid gap-2 text-amber-50">
                      <div className="flex items-center flex-row justify-between">
                        <Label htmlFor="password">Password</Label>
                        <a
                          href="#"
                          className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                        >
                          Forgot your password?
                        </a>
                      </div>
                      <Input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)}/>
                    </div>
                  </div>
                </form>
              </CardContent>
              <CardFooter className="flex-col gap-2 ">
                <Button
                  type="submit"
                  className="w-full bg-white text-neutral-900"
                  onClick={logIn}
                >
                  Login
                </Button>
                <Button variant="outline" className="w-full hidden">
                  Login with Google
                </Button>
              </CardFooter>
            </Card>
          ) : (
            // SignUp for
            <Card className="w-[100%]  bg-transparent !p-5">
              <CardHeader>
                <CardTitle className="text-amber-50">
                  Signup to The traders studio
                </CardTitle>
                <CardDescription>
                  Enter your email and choose a password below
                </CardDescription>
                <CardAction>
                  <Button
                    variant="link"
                    className="text-amber-50"
                    onClick={() => setSignup(!signup)}
                  >
                    Login
                  </Button>
                </CardAction>
              </CardHeader>

              <CardContent className="w-[100%]">
                <form>
                  <div className="flex flex-col gap-6 w-[100%]">
                    <div className="grid gap-2 w-[100%]  text-amber-50">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="m@example.com"
                        required
                        className=""
                        onChange={(e) => setEmail(e.target.value)}
                      />
                    </div>
                    <div className="grid gap-2 text-amber-50">
                      <div className="flex items-center flex-row justify-between">
                        <Label htmlFor="password">Password</Label>
                        <a
                          href="#"
                          className="ml-auto text-sm underline-offset-4 hover:underline hidden"
                        >
                          Forgot your password?
                        </a>
                      </div>
                      <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                    </div>
                  </div>
                </form>
              </CardContent>
              <CardFooter className="flex-col gap-2 ">
                <Button
                  type="submit"
                  className="w-full bg-white text-neutral-900"
                  onClick={signUp}
                >
                  Create Account
                </Button>
                <Button variant="outline" className="w-full hidden">
                  Login with Google
                </Button>
              </CardFooter>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
function handleClick() {
  throw new Error("Function not implemented.");
}
