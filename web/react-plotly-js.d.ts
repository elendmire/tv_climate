declare module "react-plotly.js" {
  import type { Config, Data, Layout } from "plotly.js";
  import type { ComponentType, CSSProperties } from "react";

  interface PlotProps {
    data: Data[];
    layout?: Partial<Layout>;
    config?: Partial<Config>;
    style?: CSSProperties;
    className?: string;
    useResizeHandler?: boolean;
  }

  const Plot: ComponentType<PlotProps>;
  export default Plot;
}
