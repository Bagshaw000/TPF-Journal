import * as React from "react"
import { Calendar, CalendarDayButton } from "@/components/ui/calendar"

import { DateRange } from "react-day-picker"
import {
  startOfMonth,
  endOfMonth,
  eachWeekOfInterval,
  eachDayOfInterval,
  addDays,
} from "date-fns"

function getWeeks(month: Date) {
  const start = startOfMonth(month)
  const end = endOfMonth(month)

  const weeks = eachWeekOfInterval({ start, end }, { weekStartsOn: 0 })
  return weeks.map((weekStart) =>
    eachDayOfInterval({ start: weekStart, end: addDays(weekStart, 6) })
  )
}

export default function Calendar21() {
  const [range, setRange] = React.useState<DateRange | undefined>({
    from: new Date(2025, 5, 12),
    to: new Date(2025, 5, 17),
  })

  const month = range?.from ?? new Date()
  const weeks = getWeeks(month)

  // helper: weekday = $100, weekend = $220
  const getValue = (day: Date) => {
    const isWeekend = day.getDay() === 0 || day.getDay() === 6
    return isWeekend ? 220 : 100
  }

  return (
    <div className="grid grid-cols-8 w-full h-full"
      style={{
        // define the cell size for ALL children (calendar + totals col)
        ["--cell-size" as any]: "calc(100%/8)", // adjust as needed
      }}>
      {/* Calendar spans first 7 columns */}
      <div className="col-span-7">
        <Calendar
          mode="range"
          defaultMonth={month}
          selected={range}
          onSelect={setRange}
          numberOfMonths={1}
          captionLayout="dropdown"
          className="rounded-lg border shadow-sm w-full h-full [--cell-size:calc(100%/7)] grid-rows-6 !p-0"
          formatters={{
            formatMonthDropdown: (date) => {
              return date.toLocaleString("default", { month: "long" })
            },
          }}
          components={{
            DayButton: ({ children, modifiers, day, ...props }) => {
              const value = getValue(day.date)

              return (
                <CalendarDayButton
                  className="flex flex-col items-center justify-center !p-0 h-[var(--cell-size)] w-[var(--cell-size)]"
                  day={day}
                  modifiers={modifiers}
                  {...props}
                >
                  {children}
                  {!modifiers.outside && <span>${value}</span>}
                </CalendarDayButton>
              )
            },
          }}
        />
      </div>

      {/* Totals column */}
      <div className="col-span-1 flex flex-col border-l">
        {/* Header */}
        <div className="h-[var(--cell-size)] flex items-center justify-center font-semibold border-b">
        Total
        </div>
        {/* <div className="h-[var(--cell-size)] flex items-center justify-center font-semibold border-b">
          Total
        </div> */}

        {/* Weekly totals */}
        {weeks.map((week, i) => {
          const total = week.reduce((sum, day) => sum + getValue(day), 0)
          return (
            <div
              key={i}
              className="h-[var(--cell-size)] flex items-center justify-center border-b"
            >
              ${total}
            </div>
          )
        })}
      </div>
    </div>
  )
}
