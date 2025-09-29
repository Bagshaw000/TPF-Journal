'use client'

import { createContext, useState,useEffect, ReactNode } from "react";
import client  from "@/api/client";

export interface AuthContextType {
  user: any // replace `any` with your Supabase `User` type if you want
  loading: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

const AuthProvider = ({children}:{children:ReactNode})=>{
    const [user,setUser] = useState<any>(null);
    const [loading, setLoading] = useState(true)

    useEffect(()=>{
        client.auth.getSession().then(({data})=>{
            // if (data?.session?.user) {
                setUser(data?.session?.user || null)
            // }else{
            //       setUser(null );
            // }
            
            setLoading(false)
        })

        const {data:listener} = client.auth.onAuthStateChange((e,session)=>{
            setUser(session?.user||null)
        })

        return () => {
            listener.subscription.unsubscribe();
        }
    }, [])

    return <AuthContext.Provider value={{
        user, loading
    }}>{children}</AuthContext.Provider>

}

export {AuthContext,AuthProvider}