"""Virtual Stanford Research Systems SR830 lock-in amplifier (LIA) control library.

The full instrument manual, including the programming guide, can be found at
https://www.thinksrs.com/downloads/pdfs/manuals/SR830m.pdf.
"""
import warnings


class sr830:
    """Virtual Stanford Research Systems SR830 LIA instrument."""

    # --- class variables ---

    reference_sources = ("external", "internal")

    triggers = ("zero crossing", "TTL rising egde", "TTL falling edge")

    input_configurations = ("A", "A-B", "I (1 MOhm)", "I (100 MOhm)")

    groundings = ("Float", "Ground")

    input_couplings = ("AC", "DC")

    input_line_notch_filter_statuses = (
        "no filters",
        "Line notch in",
        "2 x Line notch in",
        "Both notch filters in",
    )

    sensitivities = (
        2e-9,
        5e-9,
        10e-9,
        20e-9,
        50e-9,
        100e-9,
        200e-9,
        500e-9,
        1e-6,
        2e-6,
        5e-6,
        10e-6,
        20e-6,
        50e-6,
        100e-6,
        200e-6,
        500e-6,
        1e-3,
        2e-3,
        5e-3,
        10e-3,
        20e-3,
        50e-3,
        100e-3,
        200e-3,
        500e-3,
        1.0,
    )

    reserve_modes = ("High reserve", "Normal", "Low noise")

    time_constants = (
        10e-6,
        30e-6,
        100e-6,
        300e-6,
        1e-3,
        3e-3,
        10e-3,
        30e-3,
        100e-3,
        300e-3,
        1.0,
        3.0,
        10.0,
        30.0,
        100.0,
        300.0,
        1e3,
        3e3,
        10e3,
        30e3,
    )

    low_pass_filter_slopes = (6, 12, 18, 24)

    synchronous_filter_statuses = ("Off", "below 200 Hz")

    display_ch1 = ("X", "R", "X Noise", "Aux In 1", "Aux In 2")

    display_ch2 = ("Y", "Phase", "Y Noise", "Aux In 3", "Aux In 4")

    ratio_ch1 = ("none", "Aux In 1", "Aux In 2")

    ratio_ch2 = ("none", "Aux In 3", "Aux In 4")

    front_panel_output_sources_ch1 = ("CH1 display", "X")

    front_panel_output_sources_ch2 = ("CH2 display", "Y")

    expands = (0, 10, 100)

    output_interfaces = ("RS232", "GPIB")

    key_click_states = ("Off", "On")

    alarm_statuses = ("Off", "On")

    sample_rates = (
        62.5e-3,
        125e-3,
        250e-3,
        500e-3,
        1,
        2,
        4,
        8,
        16,
        32,
        64,
        128,
        256,
        512,
        "Trigger",
    )

    end_of_buffer_modes = ("1 Shot", "Loop")

    trigger_start_modes = ("Off", "Start scan")

    data_transfer_modes = ("Off", "On (DOS)", "On (Windows)")

    local_modes = ("Local", "Remote", "Local lockout")

    gpib_override_remote_conditions = ("No", "Yes")

    # --- private class variables ---

    _enable_register_cmd_dict = {
        "standard_event": "*ESE",
        "serial_poll": "*SRE",
        "error": "ERRE",
        "lia_status": "LIAE",
    }

    _status_byte_cmd_dict = {
        "standard_event": "*ESR?",
        "serial_poll": "*STB?",
        "error": "ERRS?",
        "lia_status": "LIAS?",
    }

    # Meaning of status bits. Indices of outer list are same are bit numbers.
    # Indices of inner lists give description of event or state.
    _serial_poll_status_bit_names = [
        "SCN",
        "IFC",
        "ERR",
        "LIA",
        "MAV",
        "ESB",
        "SRQ",
        "Unused",
    ]
    _serial_poll_status_byte = [
        ["", "No scan in progress"],
        ["", "No command execution in progress"],
        ["", "An enabled bit in error status byte has been set"],
        ["", "An enabled bit in LIA status byte has been set"],
        ["", "Interface output buffer is non-empty"],
        ["", "An enabled bit in standard status byte has been set"],
        ["", "A service request has occured"],
        ["", ""],
    ]

    _standard_event_status_bit_names = [
        "INP",
        "Unused",
        "QRY",
        "Unused",
        "EXE",
        "CMD",
        "URQ",
        "PON",
    ]
    _standard_event_status_byte = [
        ["", "Input queue overflow"],
        ["", ""],
        ["", "Output queue overflow"],
        ["", ""],
        ["", "Command cannot execute/parameter out of range"],
        ["", "Received illegal command"],
        ["", "Key pressed/knob rotated"],
        ["", "Power-on"],
    ]

    _lia_status_bit_names = [
        "INPUT/RESRV",
        "FILTR",
        "OUTPUT",
        "UNLK",
        "RANGE",
        "TC",
        "TRIG",
        "Unused",
    ]
    _lia_status_byte = [
        ["", "Input or amplifier overload"],
        ["", "Time constant filter overload"],
        ["", "Output overload"],
        ["", "Reference unlock detected"],
        ["", "Detection frequency switched range"],
        ["", "Time constant changed indirectly"],
        ["", "Data storage triggered"],
        ["", ""],
    ]

    _error_status_bit_names = [
        "Unused",
        "Backup error",
        "RAM error",
        "Unused",
        "ROM error",
        "GPIB error",
        "DSP error",
        "Math error",
    ]
    _error_status_byte = [
        ["", ""],
        ["", "Battery backup has failed"],
        ["", "RAM memory test found error"],
        ["", ""],
        ["", "ROM memory test found error"],
        ["", "GPIB fast data transfer mode aborted"],
        ["", "DSP test found error"],
        ["", "Internal math error"],
    ]

    def __init__(self):
        """Initialise dummy properties."""
        self._set_dummy_properties()

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        self.disconnect()

    def _set_dummy_properties(self):
        """Initialise dummy properties."""
        self._errors = []
        self._reference_phase_shift = 0
        self._reference_source = 0
        self._reference_frequency = 1000
        self._reference_trigger = 0
        self._harmonic = 1
        self._sine_amplitude = 1
        self._input_configuration = 0
        self._input_shield_grounding = 0
        self._input_coupling = 0
        self._line_notch_filter_status = 0
        self._sensitivity = 26
        self._reserve_mode = 1
        self._time_constant = 8
        self._lowpass_filter_slope = 1
        self._sync_filter_status = 0
        self._output_interface = 0
        self._ch1_display = 0
        self._ch1_ratio = 0
        self._ch2_display = 0
        self._ch2_ratio = 0
        self._ch1_output = 0
        self._ch2_output = 0
        self._X_offset = 0
        self._X_expand = 0
        self._Y_offset = 0
        self._Y_expand = 0
        self._R_offset = 0
        self._R_expand = 0
        self._aux_out_1 = 0
        self._aux_out_2 = 0
        self._aux_out_3 = 0
        self._aux_out_4 = 0
        self._key_click_state = 0
        self._alarm_status = 0
        self._sample_rate = 13
        self._end_of_buffer_mode = 0
        self._trigger_start_mode = 0
        self._buffer_size = 0
        self._data_transfer_mode = 0
        self._idn = "Dummy_Stanford_Research_Systems,SR830,s/n00000,ver0.000"
        self._local_mode = 0
        self._gpib_override_remote = 0
        self._power_on_status_clear_bit = 0

    def connect(
        self,
        resource_name,
        resource_manager=None,
        output_interface=0,
        reset=True,
        local_lockout=True,
        **resource_kwargs,
    ):
        """Conntect to the instrument.

        Creates the `instr` attribute, which provides access to all low-level PyVISA
        attributes and methods. This can be used to read the resource name, for
        example.

        Parameters
        ----------
        resource_name : str
            Full VISA resource name, e.g. "ASRL2::INSTR", "GPIB0::14::INSTR" etc. See
            https://pyvisa.readthedocs.io/en/latest/introduction/names.html for more
            info on correct formatting for resource names.
        resource_manager : visa.ResourceManager, optional
            Resource manager used to create new connection. If `None`, create a new
            resource manager using system set VISA backend.
        output_interface : {0, 1}, optional
            Communication interface on the lock-in amplifier rear panel used to read
            instrument responses. Default it RS232. Although the SR830 can read
            commands from both interfaces at any time, it can only send responses over
            one. This does not need to match the VISA resource interface type if, for
            example, an interface adapter is used between the control computer and the
            instrument. Valid output communication interfaces:

                * 0 : RS232
                * 1 : GPIB

        reset : bool, optional
            Reset the instrument to the built-in default configuration.
        local_lockout : bool, optional
            If True all front panel keys are disabled, including the 'Local' key. If
            False all keys except the 'Local' key are disabled, which the user may
            press to manually return the instrument to local control.
        resource_kwargs : dict
            Keyword arguments passed to PyVISA resource to be used to change
            instrument attributes after construction.
        """
        self.output_interface = output_interface

        if local_lockout is True:
            self.local_mode = 2
        else:
            self.local_mode = 1

    def disconnect(self):
        """Disconnect the instrument after returning to local mode."""
        pass

    def enable_all_status_bytes(self):
        """Enable all status bytes."""
        pass

    @property
    def errors(self):
        """Check for errors.

        Returns
        -------
        errors : list
            List of errors.
        """
        return self._errors

    # --- Reference and phase commands ---
    @property
    def reference_phase_shift(self):
        """Get the reference phase shift.

        Returns
        -------
        phase_shift : float
            Phase shift in degrees, -360 =< phase_shift =< 720.
        """
        return self._reference_phase_shift

    @reference_phase_shift.setter
    def reference_phase_shift(self, phase_shift):
        """Set the reference phase shift.

        Parameters
        ----------
        phase_shift : float
            Phase shift in degrees, -360 =< phase_shift =< 720.
        """
        if (phase_shift >= -360) and (phase_shift <= 720):
            self._reference_phase_shift = phase_shift
        else:
            raise ValueError(
                f"Invalid phase shift: {phase_shift}. Must be in range -360 - 720 "
                + "degrees."
            )

    @property
    def reference_source(self):
        """Get the reference source.

        Returns
        -------
        source : {0, 1}
            Refernce source:

                * 0 : external
                * 1 : internal
        """
        return self._reference_source

    @reference_source.setter
    def reference_source(self, source):
        """Set the reference source.

        Parameters
        ----------
        source : {0, 1}
            Refernce source:

                * 0 : external
                * 1 : internal
        """
        if source in [0, 1]:
            self._reference_source = source
        else:
            raise ValueError(
                f"Invalid reference source: {source}. Must be 0 (external) or 1 "
                + "(internal)."
            )

    @property
    def reference_frequency(self):
        """Get the reference frequency.

        Returns
        -------
        freq : float
            Frequency in Hz, 0.001 =< freq =< 102000.
        """
        return self._reference_frequency

    @reference_frequency.setter
    def reference_frequency(self, freq):
        """Set the frequency of the internal oscillator.

        Parameters
        ----------
        freq : float
            Frequency in Hz, 0.001 =< freq =< 102000.
        """
        if (freq >= 0.001) and (freq <= 102000):
            self._reference_frequency = freq
        else:
            raise ValueError(
                f"Invalid reference frequency: {freq}. Must be in range 0.001 - 102000 "
                + "Hz."
            )

    @property
    def reference_trigger(self):
        """Get the reference trigger type when using external ref.

        Returns
        -------
        trigger : {0, 1, 2}
            Trigger type:

                * 0: zero crossing
                * 1: TTL rising egde
                * 2: TTL falling edge
        """
        return self._reference_trigger

    @reference_trigger.setter
    def reference_trigger(self, trigger):
        """Set the reference trigger type when using external ref.

        Parameters
        ----------
        trigger : {0, 1, 2}
            Trigger type:

                * 0: zero crossing
                * 1: TTL rising egde
                * 2: TTL falling edge
        """
        if trigger in [0, 1, 2]:
            self._reference_trigger = trigger
        else:
            raise ValueError(
                f"Invalid trigger type: {trigger}. Must be 0 (zero crossing), 1 "
                + "(rising edge), or 2 (falling edge)."
            )

    @property
    def harmonic(self):
        """Get detection harmonic.

        Returns
        -------
        harmonic : int
            detection harmonic, 1 =< harmonic =< 19999
        """
        return self._harmonic

    @harmonic.setter
    def harmonic(self, harmonic):
        """Set detection harmonic.

        Parameters
        ----------
        harmonic : int
            Detection harmonic, 1 =< harmonic =< 19999.
        """
        if (harmonic >= 1) and (harmonic <= 19999):
            self._harmonic = harmonic
        else:
            raise ValueError(
                f"Invalid detection harmonic: {harmonic}. Must be in range 1 - 19999."
            )

    @property
    def sine_amplitude(self):
        """Get the amplitude of the sine output.

        Returns
        -------
        amplitude : float
            sine amplitude in volts, 0.004 =< amplitude =< 5.000
        """
        return self._sine_amplitude

    @sine_amplitude.setter
    def sine_amplitude(self, amplitude):
        """Set the amplitude of the sine output.

        Parameters
        ----------
        amplitude : float
            sine amplitude in volts, 0.004 =< amplitude =< 5.000
        """
        if (amplitude >= 0.004) and (amplitude <= 5):
            self._sine_amplitude = amplitude
        else:
            raise ValueError(
                f"Invalid sine output amplitude: {amplitude}. Must be in range 0.004 -"
                + " 5 volts."
            )

    @property
    def input_configuration(self):
        """Set the input configuration.

        Returns
        -------
        config : {0, 1, 2, 3}
            Input configuration:

                * 0 : A
                * 1 : A-B
                * 2 : I (1 MOhm)
                * 3 : I (100 MOhm)
        """
        return self._input_configuration

    @input_configuration.setter
    def input_configuration(self, config):
        """Set the input configuration.

        Parameters
        ----------
        config : {0, 1, 2, 3}
            Input configuration:

                * 0 : A
                * 1 : A-B
                * 2 : I (1 MOhm)
                * 3 : I (100 MOhm)
        """
        if config in range(4):
            self._input_configuration = config
        else:
            raise ValueError(
                f"Invalid input configuration: {config}. Must be 0 (A), 1 (A-B), 2 "
                + "(I 1MOhm), or 3 (I 100MOhm)."
            )

    @property
    def input_shield_grounding(self):
        """Get input shield grounding.

        Returns
        -------
        grounding : {0, 1}
            Input shield grounding:

                * 0 : Float
                * 1 : Ground
        """
        return self._input_shield_grounding

    @input_shield_grounding.setter
    def input_shield_grounding(self, grounding):
        """Set input shield grounding.

        Parameters
        ----------
        grounding : {0, 1}
            Input shield grounding:

                * 0 : Float
                * 1 : Ground
        """
        if grounding in [0, 1]:
            self._input_shield_grounding = grounding
        else:
            raise ValueError(
                f"Invalid input shield grounding: {grounding}. Must be 0 (float) or 1"
                + " (ground)."
            )

    @property
    def input_coupling(self):
        """Get input coupling.

        Returns
        -------
        coupling : {0, 1}
            Input coupling:

                * 0 : AC
                * 1 : DC
        """
        return self._input_coupling

    @input_coupling.setter
    def input_coupling(self, coupling):
        """Set input coupling.

        Parameters
        ----------
        coupling : {0, 1}
            Input coupling:

                * 0 : AC
                * 1 : DC
        """
        if coupling in [0, 1]:
            self._input_coupling = coupling
        else:
            raise ValueError(
                f"Invalid input coupling: {coupling}. Must be 0 (AC) or 1 (DC)."
            )

    @property
    def line_notch_filter_status(self):
        """Get input line notch filter status.

        Returns
        -------
        status : {0, 1, 2, 3}
            Input line notch filter status:

                * 0 : no filters
                * 1 : Line notch in
                * 2 : 2 x Line notch in
                * 3 : Both notch filters in
        """
        return self._line_notch_filter_status

    @line_notch_filter_status.setter
    def line_notch_filter_status(self, status):
        """Set input line notch filter status.

        Parameters
        ----------
        status : {0, 1, 2, 3}
            Input line notch filter status:

                * 0 : no filters
                * 1 : Line notch in
                * 2 : 2 x Line notch in
                * 3 : Both notch filters in
        """
        if status in range(4):
            self._line_notch_filter_status = status
        else:
            raise ValueError(
                f"Invalid line notch filter status: {status}. Must be 0 (no filters), "
                + "1 (line notch in), 2 (2 x line notch in), or 3 (both line notch in)"
                + "."
            )

    # --- Gain and time constant commands ---

    @property
    def sensitivity(self):
        """Get sensitivity.

        Returns
        -------
        sensitivity : {0 - 26}
            Sensitivity in V/uA:

                * 0 : 2e-9
                * 1 : 5e-9
                * 2 : 10e-9
                * 3 : 20e-9
                * 4 : 50e-9
                * 5 : 100e-9
                * 6 : 200e-9
                * 7 : 500e-9
                * 8 : 1e-6
                * 9 : 2e-6
                * 10 : 5e-6
                * 11 : 10e-6
                * 12 : 20e-6
                * 13 : 50e-6
                * 14 : 100e-6
                * 15 : 200e-6
                * 16 : 500e-6
                * 17 : 1e-3
                * 18 : 2e-3
                * 19 : 5e-3
                * 20 : 10e-3
                * 21 : 20e-3
                * 22 : 50e-3
                * 23 : 100e-3
                * 24 : 200e-3
                * 25 : 500e-3
                * 26 : 1
        """
        return self._sensitivity

    @sensitivity.setter
    def sensitivity(self, sensitivity):
        """Set sensitivity.

        Parameters
        ----------
        sensitivity : {0 - 26}
            Sensitivity in V/uA:

                * 0 : 2e-9
                * 1 : 5e-9
                * 2 : 10e-9
                * 3 : 20e-9
                * 4 : 50e-9
                * 5 : 100e-9
                * 6 : 200e-9
                * 7 : 500e-9
                * 8 : 1e-6
                * 9 : 2e-6
                * 10 : 5e-6
                * 11 : 10e-6
                * 12 : 20e-6
                * 13 : 50e-6
                * 14 : 100e-6
                * 15 : 200e-6
                * 16 : 500e-6
                * 17 : 1e-3
                * 18 : 2e-3
                * 19 : 5e-3
                * 20 : 10e-3
                * 21 : 20e-3
                * 22 : 50e-3
                * 23 : 100e-3
                * 24 : 200e-3
                * 25 : 500e-3
                * 26 : 1
        """
        if sensitivity in range(27):
            self._sensitivity = sensitivity
        else:
            raise ValueError(
                f"Invalid sensitivity: {sensitivity}. Must be an integer in range 0 - "
                + "26."
            )

    @property
    def reserve_mode(self):
        """Get reserve mode.

        Returns
        -------
        mode : {0, 1, 2}
            Reserve mode:

                * 0 : High reserve
                * 1 : Normal
                * 2 : Low noise
        """
        return self._reserve_mode

    @reserve_mode.setter
    def reserve_mode(self, mode):
        """Set reserve mode.

        Parameters
        ----------
        mode : {0, 1, 2}
            Reserve mode:

                * 0 : High reserve
                * 1 : Normal
                * 2 : Low noise
        """
        if mode in range(3):
            self._reserve_mode = mode
        else:
            raise ValueError(
                f"Invalid reserve mode: {mode}. Must be 0 (high), 1 (normal), or 2 "
                + "(low)."
            )

    @property
    def time_constant(self):
        """Get time constant.

        Returns
        -------
        tc : {0 - 19}
            Time constant in s:

                * 0 : 10e-6
                * 1 : 30e-6
                * 2 : 100e-6
                * 3 : 300e-6
                * 4 : 1e-3
                * 5 : 3e-3
                * 6 : 10e-3
                * 7 : 30e-3
                * 8 : 100e-3
                * 9 : 300e-3
                * 10 : 1
                * 11 : 3
                * 12 : 10
                * 13 : 30
                * 14 : 100
                * 15 : 300
                * 16 : 1e3
                * 17 : 3e3
                * 18 : 10e3
                * 19 : 30e3
        """
        return self._time_constant

    @time_constant.setter
    def time_constant(self, tc):
        """Set time constant.

        Parameters
        ----------
        tc : {0 - 19}
            Time constant in s:

                * 0 : 10e-6
                * 1 : 30e-6
                * 2 : 100e-6
                * 3 : 300e-6
                * 4 : 1e-3
                * 5 : 3e-3
                * 6 : 10e-3
                * 7 : 30e-3
                * 8 : 100e-3
                * 9 : 300e-3
                * 10 : 1
                * 11 : 3
                * 12 : 10
                * 13 : 30
                * 14 : 100
                * 15 : 300
                * 16 : 1e3
                * 17 : 3e3
                * 18 : 10e3
                * 19 : 30e3
        """
        if tc in range(20):
            self._time_constant = tc
        else:
            raise ValueError(
                f"Invalid time constant: {tc}. Must be an integer in range 0 - 19."
            )

    @property
    def lowpass_filter_slope(self):
        """Get the low pass filter slope.

        Parameters
        ----------
        slope : {0, 1, 2, 3}
            Low pass filter slope in dB/oct:

                * 0 : 6
                * 1 : 12
                * 2 : 18
                * 3 : 24
        """
        return self._lowpass_filter_slope

    @lowpass_filter_slope.setter
    def lowpass_filter_slope(self, slope):
        """Set the low pass filter slope.

        Parameters
        ----------
        slope : {0, 1, 2, 3}
            Low pass filter slope in dB/oct:

                * 0 : 6
                * 1 : 12
                * 2 : 18
                * 3 : 24
        """
        if slope in range(4):
            self._lowpass_filter_slope = slope
        else:
            raise ValueError(
                f"Invalid low-pass filter slope: {slope}. Must be 0 (6 dB/oct), 1 "
                + "(12 dB/oct), 2 (18 dB/oct), or 3 (24 dB/oct)."
            )

    @property
    def sync_filter_status(self):
        """Get synchronous filter status.

        Returns
        -------
        status : {0, 1}
            Synchronous filter status:

                * 0 : Off
                * 1 : below 200 Hz
        """
        return self._sync_filter_status

    @sync_filter_status.setter
    def sync_filter_status(self, status):
        """Set synchronous filter status.

        Parameters
        ----------
        status : {0, 1}
            Synchronous filter status:

                * 0 : Off
                * 1 : below 200 Hz
        """
        if status in [0, 1]:
            self._sync_filter_status = status
        else:
            raise ValueError(
                f"Invalid synchronous filter status: {status}. Must be 0 (off) or 1 "
                + "(below 200 Hz)."
            )

    # --- Display and output commands ---

    @property
    def output_interface(self):
        """Get the output communication interface.

        Returns
        -------
        interface : {0, 1}
            Output communication interface:

                * 0 : RS232
                * 1 : GPIB
        """
        return self._output_interface

    @output_interface.setter
    def output_interface(self, interface):
        """Set the output communication interface.

        This command should be sent before any query commands to direct the
        responses to the interface in use.

        Parameters
        ----------
        interface : {0, 1}
            Output communication interface:

                * 0 : RS232
                * 1 : GPIB
        """
        if interface in [0, 1]:
            self._output_interface = interface
        else:
            raise ValueError(
                f"Invalid output interface: {interface}. Must be 0 (RS232) or 1 "
                + "(GPIB)."
            )

    def set_display(self, channel, display=1, ratio=0):
        """Set a channel display configuration.

        Parameters
        ----------
        channel : {1, 2}
            Channel:

                * 1 : CH1
                * 2 : CH2

        display : {0, 1, 2, 3, 4}
            Display parameter for CH1:

                * 0 : X
                * 1 : R
                * 2 : X Noise
                * 3 : Aux In 1
                * 4 : Aux In 2;

            Display parameter for CH2:

                * 0 : Y
                * 1 : Phase
                * 2 : Y Noise
                * 3 : Aux In 3
                * 4 : Aux In 4

        ratio : {0, 1, 2}
            Ratio type for CH1:

                * 0 : none
                * 1 : Aux In 1
                * 2 : Aux In 2

            Ratio type for CH2:

                * 0 : none
                * 1 : Aux In 3
                * 2 : Aux In 4
        """
        if (channel in [1, 2]) and (display in range(5)) and (ratio in range(3)):
            if channel == 1:
                self._ch1_display = display
                self._ch1_ratio = ratio
            elif channel == 2:
                self._ch2_display = display
                self._ch2_ratio = ratio
        else:
            raise ValueError(
                f"Invalid channel, display, or ratio: {channel}, {display}, or {ratio}"
                + ". Channel must be 1 (Ch1) or 2 (Ch2); display must be an integer in"
                + " range 0 - 4; and ratio must be an integer in the range 0 - 2."
            )

    def get_display(self, channel):
        """Get a channel display configuration.

        Parameters
        ----------
        channel : {1, 2}
            Channel:

                * 1 : CH1
                * 2 : CH2

        Returns
        -------
        display : {0, 1, 2, 3, 4}
            Display parameter for CH1:

                * 0 : X
                * 1 : R
                * 2 : X Noise
                * 3 : Aux In 1
                * 4 : Aux In 2;

            Display parameter for CH2:

                * 0 : Y
                * 1 : Phase
                * 2 : Y Noise
                * 3 : Aux In 3
                * 4 : Aux In 4

        ratio : {0, 1, 2}
            Ratio type for CH1:

                * 0 : none
                * 1 : Aux In 1
                * 2 : Aux In 2

            Ratio type for CH2:

                * 0 : none
                * 1 : Aux In 2
                * 2 : Aux In 4
        """
        if channel == 1:
            return self._ch1_display, self._ch1_ratio
        elif channel == 2:
            return self._ch2_display, self._ch2_ratio
        else:
            raise ValueError(f"Invalid channel: {channel}. Must be 0 (Ch1) or 1 (Ch2).")

    def set_front_output(self, channel, output=0):
        """Set front panel output sources.

        Parameters
        ----------
        channel : {1, 2}
            Channel:

                * 1 : CH1
                * 2 : CH2

        output : {0, 1}
            Output quantity for CH1:

                * 0 : CH1 display
                * 1 : X

            Output quantity for CH2:

                * 0 : CH2 display
                * 1 : Y
        """
        if (channel in [1, 2]) and (output in [0, 1]):
            if channel == 1:
                self._ch1_output = output
            elif channel == 2:
                self._ch2_output = output
        else:
            raise ValueError(
                f"Invalid channel or output: {channel} or {output}. Channel must be 0 "
                + "(Ch1) or 1 (Ch2); and output must be 0 or 1."
            )

    def get_front_output(self, channel):
        """Get front panel output sources.

        Parameters
        ----------
        channel : {1, 2}
            Channel:

                * 1 : CH1
                * 2 : CH2

        Returns
        -------
        output : {0, 1}
            Output quantity for CH1:

                * 0 : CH1 display
                * 1 : X

            Output quantity for CH2:

                * 0 : CH2 display
                * 1 : Y
        """
        if channel == 1:
            return self._ch1_output
        elif channel == 2:
            return self._ch2_output
        else:
            raise ValueError(f"Invalid channel: {channel}. Must be 0 (Ch1) or 1 (Ch2).")

    def set_output_offset_expand(self, parameter, offset, expand):
        """Set the output offsets and expands.

        Setting an offset to zero turns the offset off.

        Parameters
        ----------
        parameter : {1, 2, 3}
            Measurement parameter:

                * 1 : X
                * 2 : Y
                * 3 : R

        offset : float
            Offset in %, -105.00 =< offset =< 105.00.
        expand : {0, 1, 2}
            Expand:

                * 0 : 0
                * 1 : 10
                * 2 : 100
        """
        if (
            (parameter in [1, 2, 3])
            and (offset >= -105)
            and (offset <= 105)
            and (expand in range(3))
        ):
            if parameter == 1:
                self._X_offset = offset
                self._X_expand = expand
            elif parameter == 2:
                self._Y_offset = offset
                self._Y_expand = expand
            elif parameter == 3:
                self._R_offset = offset
                self._R_expand = expand
        else:
            raise ValueError(
                f"Invalid parameter, offset, or expand: {parameter}, {offset}, or "
                + f"{expand}. Parameter must be 1 (X), 2 (Y), or 3 (R); offset must "
                + "be in the range -105 - 105 percent; and expand must be 0 (0), 1 "
                + "(10), or 2 (100)."
            )

    def get_output_offset_expand(self, parameter):
        """Get the output offsets and expands.

        Parameters
        ----------
        parameter : {1, 2, 3}
            Measurement parameter:

                * 1 : X
                * 2 : Y
                * 3 : R

        Returns
        -------
        offset : float
            Offset in %, -105.00 =< offset =< 105.00.
        expand : {0, 1, 2}
            Expand:

                * 0 : 0
                * 1 : 10
                * 2 : 100
        """
        if parameter == 1:
            return self._X_offset, self._X_expand
        elif parameter == 2:
            return self._Y_offset, self._Y_expand
        elif parameter == 3:
            return self._R_offset, self._R_expand
        else:
            raise ValueError(
                f"Invalid paramter: {parameter}. Must be 1 (X), 2 (Y), or 3 (R)."
            )

    def auto_offset(self, parameter):
        """Set parameter offset to zero.

        Paramaters
        ----------
        parameter : {1, 2, 3}
            Measurement parameter:

                * 1 : X
                * 2 : Y
                * 3 : R
        """
        if parameter == 1:
            self._X_offset = 0
        elif parameter == 2:
            self._Y_offset = 0
        elif parameter == 3:
            self._R_offset = 0
        else:
            raise ValueError(
                f"Invalid paramter: {parameter}. Must be 1 (X), 2 (Y), or 3 (R)."
            )

    # --- Aux input and output commands ---

    def get_aux_in(self, aux_in):
        """Get voltage of auxiliary input.

        The resolution is 1/3 mV.

        Parameter
        ---------
        aux_in : {1, 2, 3, 4}
            Auxiliary input (1, 2, 3, or 4).

        Returns
        -------
        voltage : float
            Auxiliary input voltage.
        """
        if aux_in in [1, 2, 3, 4]:
            return 1
        else:
            raise ValueError(
                f"Invalid auxilliary input: {aux_in}. Must be an integer in range "
                + "1 - 4."
            )

    def set_aux_out(self, aux_out, voltage):
        """Set voltage of auxiliary output.

        Parameters
        ----------
        aux_out : {1, 2, 3, 4}
            Auxiliary output (1, 2, 3, or 4).
        voltage : float
            Output voltage, -10.500 =< voltage =< 10.500
        """
        if (aux_out in [1, 2, 3, 4]) and (voltage >= -10.5) and (voltage <= 10.5):
            if aux_out == 1:
                self._aux_out_1 = voltage
            elif aux_out == 2:
                self._aux_out_2 = voltage
            elif aux_out == 3:
                self._aux_out_3 = voltage
            elif aux_out == 4:
                self._aux_out_4 = voltage
        else:
            raise ValueError(
                f"Invalid auxilliary output or voltage: {aux_out} or {voltage}. Aux "
                + "out must be an integer in range 1 - 4, and voltage must be in "
                + "range -10.5 - 10.5 volts."
            )

    def get_aux_out(self, aux_out):
        """Get voltage of auxiliary output.

        Parameters
        ----------
        aux_out : {1, 2, 3, 4}
            Auxiliary output (1, 2, 3, or 4).

        Returns
        -------
        voltage : float
            Output voltage, -10.500 =< voltage =< 10.500
        """
        if aux_out == 1:
            return self._aux_out_1
        elif aux_out == 2:
            return self._aux_out_2
        elif aux_out == 3:
            return self._aux_out_3
        elif aux_out == 4:
            return self._aux_out_4
        else:
            raise ValueError(
                f"Invalid auxilliary output: {aux_out}. Must be an integer in range "
                + "1 - 4."
            )

    # --- Setup commands ---

    @property
    def key_click_state(self):
        """Get key click state.

        Returns
        -------
        state : {0, 1}
            Key click state:

                * 0 : Off
                * 1 : On
        """
        return self._key_click_state

    @key_click_state.setter
    def key_click_state(self, state):
        """Set key click state.

        Parameters
        ----------
        state : {0, 1}
            Key click state:

                * 0 : Off
                * 1 : On
        """
        if state in [0, 1]:
            self._key_click_state = state
        else:
            raise ValueError(
                f"Invalid key click state: {state}. Must be 0 (off) or 1 (on)."
            )

    @property
    def alarm_status(self):
        """Get the alarm status.

        The 'alarm' refers to all sounds emitted by the instrument.

        Returns
        -------
        status : {0, 1}
            Alarm status:

                * 0 : Off
                * 1 : On
        """
        return self._alarm_status

    @alarm_status.setter
    def alarm_status(self, status):
        """Set the alarm status.

        The 'alarm' refers to all sounds emitted by the instrument.

        Parameters
        ----------
        status : {0, 1}
            Alarm status:

                * 0 : Off
                * 1 : On
        """
        if status in [0, 1]:
            self._alarm_status = status
        else:
            raise ValueError(
                f"Invalid alarm status: {status}. Must be 0 (off) or 1 (on)."
            )

    def save_setup(self, number):
        """Save the lock-in setup in a settings buffer.

        Parameters
        ----------
        number : {1 - 9}
            Buffer number, 1 =< number =< 9.
        """
        if number in range(1, 10):
            pass
        else:
            raise ValueError(
                f"Invalid save buffer number: {number}. Must be an integer in range "
                + "1 - 9."
            )

    def recall_setup(self, number):
        """Recall lock-in setup from setting buffer.

        Parameters
        ----------
        number : {1 - 9}
            Buffer number, 1 =< number =< 9.
        """
        if number in range(1, 10):
            pass
        else:
            raise ValueError(
                f"Invalid save buffer number: {number}. Must be an integer in range "
                + "1 - 9."
            )

    # --- Auto functions ---

    def auto_gain(self):
        """Automatically set the gain.

        Does nothing if the time constant is greater than 1 second.
        """
        pass

    def auto_reserve(self):
        """Automatically set reserve."""
        pass

    def auto_phase(self):
        """Automatically set phase."""
        pass

    # --- Data storage commands ---

    @property
    def sample_rate(self):
        """Get the data sample rate.

        Returns
        ---------
        rate : {0 - 14} or float or int or "Trigger"
            Sample rate in Hz:

                * 0 : 62.5e-3
                * 1 : 125e-3
                * 2 : 250e-3
                * 3 : 500e-3
                * 4 : 1
                * 5 : 2
                * 6 : 4
                * 7 : 8
                * 8 : 16
                * 9 : 32
                * 10 : 64
                * 11 : 128
                * 12 : 256
                * 13 : 512
                * 14 : Trigger
        """
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, rate):
        """Set the data sample rate.

        Paramters
        ---------
        rate : {0 - 14}
            Sample rate in Hz:

                * 0 : 62.5e-3
                * 1 : 125e-3
                * 2 : 250e-3
                * 3 : 500e-3
                * 4 : 1
                * 5 : 2
                * 6 : 4
                * 7 : 8
                * 8 : 16
                * 9 : 32
                * 10 : 64
                * 11 : 128
                * 12 : 256
                * 13 : 512
                * 14 : Trigger
        """
        if rate in range(15):
            self._sample_rate = rate
        else:
            raise ValueError(
                f"Invalid sample rate: {rate}. Must be an integer in range 0 - 14."
            )

    @property
    def end_of_buffer_mode(self):
        """Get the end of buffer mode.

        Returns
        ----------
        mode : {0, 1} or str
            End of buffer mode:

                * 0 : 1 Shot
                * 1 : Loop
        """
        return self._end_of_buffer_mode

    @end_of_buffer_mode.setter
    def end_of_buffer_mode(self, mode):
        """Set the end of buffer mode.

        If Loop mode is used, make sure to pause data storage before reading the
        data to avoid confusion about which point is the most recent.

        Parameters
        ----------
        mode : {0, 1}
            End of buffer mode:

                * 0 : 1 Shot
                * 1 : Loop
        """
        if mode in [0, 1]:
            self._end_of_buffer_mode = mode
        else:
            raise ValueError(
                f"Invalid end of buffer mode: {mode}. Must be 0 (1 shot) or 1 (loop)."
            )

    def trigger(self):
        """Send software trigger."""
        pass

    @property
    def trigger_start_mode(self):
        """Get the trigger start mode.

        Returns
        -------
        mode : {0, 1} or str
            Trigger start mode:

                * 0 : Off
                * 1 : Start scan
        """
        return self._trigger_start_mode

    @trigger_start_mode.setter
    def trigger_start_mode(self, mode):
        """Set the trigger start mode.

        Parameters
        ----------
        mode : {0, 1}
            Trigger start mode:

                * 0 : Off
                * 1 : Start scan
        """
        if mode in [0, 1]:
            self._trigger_start_mode = mode
        else:
            raise ValueError(
                f"Invalid trigger start mode: {mode}. Must be 0 (off) or 1 "
                + "(start scan)."
            )

    def start(self):
        """Start or resume data storage.

        Ignored if storage already in progress.

        After turning on fast data transfer, this function starts the scan after a
        delay of 0.5 sec.
        """
        # TODO: implement dummy store in buffer
        pass

    def pause(self):
        """Pause data storage.

        Ignored if storage is already paused or reset.
        """
        # TODO: implement dummy store in buffer
        pass

    def reset_data_buffers(self):
        """Reset data buffers.

        This command will erase the data buffer.
        """
        # TODO: implement dummy store in buffer
        pass

    # --- Data transfer commands ---

    def measure(self, parameter):
        """Read the value of X, Y, R, or phase.

        Parameters
        ----------
        parameter : {1, 2, 3, 4}
            Measured parameter:

                * 1 : X
                * 2 : Y
                * 3 : R
                * 4 : Phase

        Returns
        -------
        value : float
            Value of measured parameter in volts or degrees.
        """
        if parameter in range(1, 5):
            return 1.0
        else:
            raise ValueError(
                f"Invalid parameter: {parameter}. Must be 1 (X), 2 (Y), 3 (R), or 4 "
                + "(phase)."
            )

    def read_display(self, channel):
        """Read the value of a channel display.

        Parameters
        ----------
        channel : {1, 2}
            Channel display to read:

                * 1 : CH1
                * 2 : CH2

        Returns
        -------
        value : float
            Displayed value in display units.
        """
        if channel in [1, 2]:
            return 1.0
        else:
            raise ValueError(f"Invalid channel: {channel}. Must be 0 (Ch1) or 1 (Ch2).")

    def measure_multiple(self, parameters):
        """Read multiple (2-6) parameter values simultaneously.

        The values of X and Y are recorded at a single instant.
        The values of R and phase are also recorded at a single
        instant. Thus reading X,Y OR R,phase yields a coherent snapshot
        of the output signal. If X,Y,R and phase are all read, then the
        values of X,Y are recorded approximately 10µs apart from
        R,phase. Thus, the values of X and Y may not yield the exact
        values of R and phase from a single SNAP? query.

        The values of the Aux Inputs may have an uncertainty of up to
        32µs. The frequency is computed only every other period or 40 ms,
        whichever is longer.

        Paramters
        ---------
        paramters : list or tuple of int
            Parameters to measure:

                * 1 : X
                * 2 : Y
                * 3 : R
                * 4 : Phase
                * 5 : Aux In 1
                * 6 : Aux In 2
                * 7 : Aux In 3
                * 8 : Aux In 4
                * 9 : Ref Frequency
                * 10 : CH1 display
                * 11 : CH2 display

        Returns
        -------
        values : tuple of float
            Values of measured parameters.
        """
        if all(p in range(1, 12) for p in parameters) and (
            len(parameters) in range(2, 7)
        ):
            return (1.0 for i in parameters)
        else:
            raise ValueError(
                f"Invalid parameter list: {parameters}. All paramters must be integers"
                + " in the range 1 - 11 and the list length must be in the range 2 - 6"
                + "."
            )

    @property
    def buffer_size(self):
        """Get the number of points stored in the buffer.

        Returns
        -------
        N : int
            Number of points in the buffer.
        """
        return self._buffer_size

    def get_ascii_buffer_data(self, channel, start_bin, bins):
        """Get the points stored in a channel buffer range.

        The values are returned as ASCII floating point numbers with
        the units of the trace.

        Bins (or points) a labelled from 0 (oldest) to N-1 (newest)
        where N is the total number of bins.

        If data storage is set to Loop mode, storage is paused before
        reading any data. This is because the points are indexed relative
        to the most recent point which is continually changing.

        Parameters
        ----------
        channel : {1, 2}
            Channel 1 or 2.
        start_bin : int
            Starting bin to read where 0 is oldest. Must be in range 0 - 16382.
        bins : int
            Number of bins to read. Must be in range 1 - 16383.

        Returns
        -------
        buffer : tuple of float
            Data stored in buffer range.
        """
        if (
            (channel in range(3))
            and (start_bin in range(16383))
            and (bins in range(1, 16384))
        ):
            return tuple([1.0 for x in range(bins)])
        else:
            raise ValueError(
                f"Invalid channel, start bin or bins: {channel}, {start_bin}, or "
                + f"{bins}. Channel must be 1 (Ch1) or 2 (Ch2); start bin must in "
                + "range 0 - 16382; and bins must be in range 1 - 16383."
            )

    def get_binary_buffer_data(self, channel, start_bin, bins):
        """Get the points stored in a channel buffer range.

        The values are returned as IEEE format binary floating point
        numbers with the units of the trace.

        Bins (or points) a labelled from 0 (oldest) to N-1 (newest)
        where N is the total number of bins.

        If data storage is set to Loop mode, storage is paused before
        reading any data. This is because the points are indexed relative
        to the most recent point which is continually changing.

        Parameters
        ----------
        channel : {1, 2}
            Channel 1 or 2.
        start_bin : int
            Starting bin to read where 0 is oldest. Must be in range 0 - 16382.
        bins : int
            Number of bins to read. Must be in range 1 - 16383.

        Returns
        -------
        buffer : tuple of float
            Data stored in buffer range.
        """
        if (
            (channel in [1, 2])
            and (start_bin >= 0)
            and (start_bin <= 16382)
            and (bins >= 1)
            and (bins <= 16383)
        ):
            return tuple([1.0 for x in range(bins)])
        else:
            raise ValueError(
                f"Invalid channel, start bin or bins: {channel}, {start_bin}, or "
                + f"{bins}. Channel must be 1 (Ch1) or 2 (Ch2); start bin must in "
                + "range 0 - 16382; and bins must be in range 1 - 16383."
            )

    def get_non_norm_buffer_data(self, channel, start_bin, bins):
        """Get the points stored in a channel buffer range.

        The values are returned as non-normalised floating point
        numbers with the units of the trace.

        Bins (or points) a labelled from 0 (oldest) to N-1 (newest)
        where N is the total number of bins.

        If data storage is set to Loop mode, make sure that
        storage is paused before reading any data. This is because
        the points are indexed relative to the most recent point
        which is continually changing.

        Parameters
        ----------
        channel : {1, 2}
            Channel 1 or 2.
        start_bin : int
            Starting bin to read where 0 is oldest. Must be in range 0 - 16382.
        bins : int
            Number of bins to read. Must be in range 1 - 16383.

        Returns
        -------
        buffer : tuple of float
            Data stored in buffer range.
        """
        if (
            (channel in [1, 2])
            and (start_bin >= 0)
            and (start_bin <= 16382)
            and (bins >= 1)
            and (bins <= 16383)
        ):
            return tuple([1.0 for x in range(bins)])
        else:
            raise ValueError(
                f"Invalid channel, start bin or bins: {channel}, {start_bin}, or "
                + f"{bins}. Channel must be 1 (Ch1) or 2 (Ch2); start bin must in "
                + "range 0 - 16382; and bins must be in range 1 - 16383."
            )

    @property
    def data_transfer_mode(self):
        """Get the data transfer mode.

        Returns
        -------
        mode : {0, 1, 2}
            Data transfer mode:

                * 0 : Off
                * 1 : On (DOS)
                * 2 : On (Windows)
        """
        return self._data_transfer_mode

    @data_transfer_mode.setter
    def data_transfer_mode(self, mode):
        """Set the data transfer mode.

        GPIB only.

        Parameters
        ----------
        mode : {0, 1, 2}
            Data transfer mode:

                * 0 : Off
                * 1 : On (DOS)
                * 2 : On (Windows)
        """
        if mode in range(3):
            self._data_transfer_mode = mode
        else:
            raise ValueError(
                f"Invalid data transfer mode: {mode}. Must be 0 (off), 1 (on [DOS]), "
                + "or 2 (on [Windows])."
            )

    # --- Interface commands ---

    def reset(self):
        """Reset the instrument to the default configuration."""
        self._set_dummy_properties()

    @property
    def idn(self):
        """Get the device identification string.

        The string is in the format "Stanford_Research_Systems,SR830,s/n00111,ver1.000",
        where, for example, the serial number is 00111 and the firmware version is
        1.000.

        Returns
        -------
        idn : list
            List of identification strings consisting of manufacturer, model, serial
            number, and firmware version number in order.
        """
        return self._idn

    @property
    def local_mode(self):
        """Get the local/remote function.

        Returns
        -------
        local : {0, 1, 2}
            Local/remote function:

                * 0 : LOCAL
                * 1 : REMOTE
                * 2 : LOCAL LOCKOUT
        """
        return self._local_mode

    @local_mode.setter
    def local_mode(self, mode):
        """Set the local/remote function.

        Parameters
        ----------
        mode : {0, 1, 2}
            Local/remote function:

                * 0 : LOCAL
                * 1 : REMOTE
                * 2 : LOCAL LOCKOUT
        """
        if mode in range(3):
            self._local_mode = mode
        else:
            raise ValueError(
                f"Invalid local mode: {mode}. Must be 0 (local), 1 (remote), or 2 "
                + "(local lockout)."
            )

    @property
    def gpib_override_remote(self):
        """Get the GPIB override remote condition.

        Under normal operation every GPIB command puts the instrument in the remote
        state with the front panel deactivated.

        Returns
        -------
        condition : int
            GPIB override remote condition:

                * 0 : No
                * 1 : Yes
        """
        return self._gpib_override_remote

    @gpib_override_remote.setter
    def gpib_override_remote(self, condition):
        """Set the GPIB override remote condition.

        Under normal operation every GPIB command puts the instrument in the remote
        state with the front panel deactivated.

        Parameters
        ----------
        condition : int
            GPIB override remote condition:

                * 0 : No
                * 1 : Yes
        """
        if condition in [0, 1]:
            self._gpib_override_remote = condition
        else:
            raise ValueError(
                f"Invalid GPIB override remote condition: {condition}. Must be 0 (no) "
                + "or 1 (yes)."
            )

    # --- Status reporting commands ---

    def clear_status_registers(self):
        """Clear all status registers."""
        pass

    def set_enable_register(self, register, value, decimal=True, bit=None):
        """Set an enable register.

        Parameters
        ----------
        register : {"standard_event", "serial_poll", "error", "lia_status"}
            Enable register to set.
        value : {0-255} or {0, 1}
            Value of standard event enable register. If decimal is true, value is in
            the range 0-255. Otherwise value is applied to a specific bit given by
            argument to 0 or 1.
        decimal : bool, optional
            If `value` is decimal or binary.
        bit : None or {0-7}, optional
            Specific bit to set with a binary value.
        """
        if register in (registers := self._enable_register_cmd_dict.keys()):
            # TODO: make dummy variables
            pass
        else:
            raise ValueError(
                f"Invalid register: {register}. Must be one of "
                + f"{', '.join(list(registers))}."
            )

    def get_enable_register(self, register, bit=None):
        """Get the standard event enable register value.

        Parameters
        ----------
        register : {"standard_event", "serial_poll", "error", "lia_status"}
            Enable register to get.
        bit : None or {0-7}, optional
            Specific bit to query. If `None`, query entire byte.

        Returns
        -------
        value : int
            Register value.
        """
        if register in (registers := self._enable_register_cmd_dict.keys()):
            # TODO: make dummy variables
            pass
        else:
            raise ValueError(
                f"Invalid register: {register}. Must be one of "
                + f"{', '.join(list(registers))}."
            )

    def get_status_byte(self, status_byte, bit=None):
        """Get a status byte.

        This function has no error check to avoid infinite recursion.

        Parameters
        ----------
        status_byte : {"standard_event", "serial_poll", "error", "lia_status"}
            Status byte to get.
        bit : None or {0-7}, optional
            Specific bit to get with a binary value. If `None` query entire byte.

        Returns
        -------
        value : int
            Status byte value.
        """
        if status_byte in (status_bytes := self._status_byte_cmd_dict.keys()):
            # TODO: make dummy variables
            pass
        else:
            raise ValueError(
                f"Invalid status byte: {status_byte}. Must be one of "
                + f"{', '.join(list(status_bytes))}."
            )

    @property
    def power_on_status_clear_bit(self):
        """Get the power-on status clear bit.

        Returns
        -------
        value : int
            Power-on status clear bit value.
        """
        return self._power_on_status_clear_bit

    @power_on_status_clear_bit.setter
    def power_on_status_clear_bit(self, value):
        """Set the power-on status clear bit.

        Parameters
        ----------
        value : {0, 1}
            Value of power-on status clear bit. Values:

                * 0 : Cleared, status enable registers maintain values at power down.
                * 1 : Set, all status and enable registers are cleared on power up.
        """
        if value in [0, 1]:
            self._power_on_status_clear_bit = value
        else:
            raise ValueError(
                f"Invalid power on status clear bit: {value}. Must be 0 (cleared) or 1"
                + " (set)."
            )
