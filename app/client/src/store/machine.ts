import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface MachineStore {
  machineId: string | null
  setMachineId: (id: string) => void
}

export const useMachineStore = create<MachineStore>()(
  persist(
    (set) => ({
      machineId: null,
      setMachineId: (id) => set({ machineId: id }),
    }),
    { name: 'sysdoc-machine' }
  )
)
