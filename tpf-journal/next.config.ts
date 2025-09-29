import { withNextVideo } from "next-video/process";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  env:{
    BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL
  }
};

export default withNextVideo(nextConfig);